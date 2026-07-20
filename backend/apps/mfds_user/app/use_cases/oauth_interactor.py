from __future__ import annotations

import secrets
from typing import Callable

from mfds_user.app.dtos.auth_dto import UserSessionDTO
from mfds_user.app.ports.input.oauth_use_case import OAuthUseCase
from mfds_user.app.ports.output.oauth_provider_port import OAuthProviderPort
from mfds_user.app.ports.output.oauth_user_repository import OAuthUserRepository
from mfds_user.app.ports.output.session_store_port import SessionStorePort
from mfds_user.app.services.token_service import generate_access_token


class OAuthInteractor(OAuthUseCase):
    def __init__(
        self,
        provider_factory: Callable[[str], OAuthProviderPort],
        user_repository: OAuthUserRepository,
        session_store: SessionStorePort,
    ) -> None:
        self._provider_factory = provider_factory
        self._user_repository = user_repository
        self._session_store = session_store

    async def build_authorize_url(self, provider: str) -> str:
        adapter = self._provider_factory(provider)  # 미지원 provider면 ValueError
        state = secrets.token_urlsafe(24)
        await self._session_store.save_state(state, provider)
        return adapter.authorize_url(state)

    async def handle_callback(self, provider: str, code: str, state: str) -> UserSessionDTO:
        saved_provider = await self._session_store.consume_state(state)
        if saved_provider != provider:
            raise ValueError("유효하지 않거나 만료된 인증 요청입니다. 다시 시도해 주세요.")

        adapter = self._provider_factory(provider)
        profile = await adapter.fetch_profile(code, state)
        if not profile.provider_id:
            raise ValueError("소셜 프로필을 가져오지 못했습니다.")

        user = await self._user_repository.upsert_social_user(profile)

        # 역할은 upsert가 화이트리스트 승격 여부로 결정해 반환한다.
        role = user.role.value
        access_token, expires_at = generate_access_token(user.id, user.email, role)
        refresh_token = secrets.token_hex(32)
        session = UserSessionDTO(
            user_id=user.id,
            email=user.email,
            name=user.name or "",
            role=role,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
        )
        await self._session_store.save(session)
        return session
