from __future__ import annotations

import os
import secrets
import time
from datetime import datetime, timezone
from typing import Callable

from auth.app.dtos.auth_dto import TokenBundle
from auth.app.ports.input.auth_use_case import IAuthUseCase
from auth.app.ports.output.identity_port import IIdentityPort
from auth.app.ports.output.oauth_provider_port import IOAuthProviderPort
from auth.app.ports.output.oauth_state_port import IOAuthStatePort
from auth.app.ports.output.refresh_session_port import IRefreshSessionPort
from auth.app.ports.output.token_issuer_port import ITokenIssuerPort
from auth.domain.value_objects import role as role_vo
from matrix.grid_seraph_token_guard_manager import TokenPayload

_DEFAULT_AUD = "foodopenlab-api"


def _aud() -> str:
    return (os.getenv("SERVICE_AUD") or _DEFAULT_AUD).strip()


class AuthInteractor(IAuthUseCase):
    """게이트웨이 오케스트레이터 — 분류·조립만, 비즈니스 규칙은 각 포트 뒤에."""

    def __init__(
        self,
        provider_factory: Callable[[str], IOAuthProviderPort],
        identity: IIdentityPort,
        token_issuer: ITokenIssuerPort,
        refresh_session: IRefreshSessionPort,
        state_store: IOAuthStatePort,
    ) -> None:
        self._provider_factory = provider_factory
        self._identity = identity
        self._token_issuer = token_issuer
        self._refresh = refresh_session
        self._state = state_store

    async def build_authorize_url(self, provider: str) -> str:
        adapter = self._provider_factory(provider)  # 미지원 provider면 ValueError
        state = secrets.token_urlsafe(24)
        await self._state.save_state(state, provider)
        return adapter.authorize_url(state)

    async def handle_callback(self, provider: str, code: str, state: str) -> TokenBundle:
        saved = await self._state.consume_state(state)
        if saved != provider:
            raise ValueError("유효하지 않거나 만료된 인증 요청입니다. 다시 시도해 주세요.")

        adapter = self._provider_factory(provider)
        profile = await adapter.fetch_profile(code, state)
        if not profile.provider_id:
            raise ValueError("소셜 프로필을 가져오지 못했습니다.")

        roles = role_vo.resolve_roles_for_email(profile.email)  # 어드민 화이트리스트 판정
        identity = await self._identity.upsert_oauth_identity(profile, roles)
        return await self._issue(identity)

    async def refresh(self, refresh_token: str) -> TokenBundle:
        rotation = await self._refresh.rotate(refresh_token)  # 재사용/무효 시 예외
        identity = await self._identity.get(rotation.sub)
        if identity is None:
            access = self._token_issuer.issue_access_token(
                rotation.sub, [role_vo.DEFAULT_ROLE.value], _aud()
            )
            return TokenBundle(
                access_token=access.token,
                refresh_token=rotation.refresh_token,
                expires_in=_expires_in(access.expires_at),
                sub=rotation.sub,
                roles=[role_vo.DEFAULT_ROLE.value],
            )
        access = self._token_issuer.issue_access_token(
            rotation.sub, identity.roles, _aud(), email=identity.email, name=identity.name
        )
        return TokenBundle(
            access_token=access.token,
            refresh_token=rotation.refresh_token,
            expires_in=_expires_in(access.expires_at),
            sub=rotation.sub,
            roles=identity.roles,
        )

    async def logout(self, current: TokenPayload, refresh_token: str | None) -> None:
        if current.jti:
            ttl = max(1, current.exp - int(time.time()))
            await self._refresh.blacklist_jti(current.jti, ttl)
        if refresh_token:
            await self._refresh.revoke(refresh_token)

    async def _issue(self, identity) -> TokenBundle:
        sub = str(identity.id)
        access = self._token_issuer.issue_access_token(
            sub, identity.roles, _aud(), email=identity.email, name=identity.name
        )
        refresh_token = await self._refresh.start(sub)
        return TokenBundle(
            access_token=access.token,
            refresh_token=refresh_token,
            expires_in=_expires_in(access.expires_at),
            sub=sub,
            roles=identity.roles,
        )


def _expires_in(expires_at: datetime) -> int:
    return max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
