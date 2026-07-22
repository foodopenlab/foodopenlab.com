"""신원 저장소 — 공유 유저 테이블(core `ExpertUserORM`)을 사용한다.

auth 자체 테이블(auth_identities) 대신 mfds_user와 동일한 `expert_users`를 upsert하므로,
토큰의 `sub`가 유저 UUID가 되어 mfds_user의 유저 스코프 엔드포인트가 그대로 동작한다.
roles(admin/user)는 여기 저장하지 않고 로그인마다 화이트리스트로 재평가해 토큰에 싣는다.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.orm.expert_user_orm import ExpertUserORM
from matrix.orm.expert_whitelist_orm import ExpertWhitelistORM

from auth.app.dtos.auth_dto import OAuthProfile
from auth.app.ports.output.identity_port import IIdentityPort
from auth.domain.entities.auth_identity_entity import AuthIdentity
from auth.domain.value_objects.role import Role, is_admin_email


class AuthIdentityRepository(IIdentityPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _resolve_roles(self, email: str) -> list[str]:
        """우선순위 admin > expert > user. admin=env, expert=DB(expert_whitelist)."""
        if is_admin_email(email):
            return [Role.ADMIN.value, Role.USER.value]
        promoted = (
            await self.session.execute(
                select(ExpertWhitelistORM.email).where(ExpertWhitelistORM.email == email)
            )
        ).scalar_one_or_none()
        if promoted:
            return [Role.EXPERT.value, Role.USER.value]
        return [Role.USER.value]

    async def upsert_oauth_identity(self, profile: OAuthProfile) -> AuthIdentity:
        email = profile.email or f"{profile.provider}_{profile.provider_id}@social.foodopenlab.local"

        # 1) (provider, provider_id) → 2) email 순으로 기존 유저 탐색
        user = (
            await self.session.execute(
                select(ExpertUserORM).where(
                    ExpertUserORM.auth_provider == profile.provider,
                    ExpertUserORM.oauth_provider_id == profile.provider_id,
                )
            )
        ).scalar_one_or_none()
        if user is None:
            user = (
                await self.session.execute(select(ExpertUserORM).where(ExpertUserORM.email == email))
            ).scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if user is None:
            user = ExpertUserORM(
                email=email,
                name=profile.name,
                picture=profile.picture,
                auth_provider=profile.provider,
                oauth_provider_id=profile.provider_id,
                hashed_password=None,
                last_login=now,
            )
            self.session.add(user)
        else:
            user.last_login = now
            if not user.oauth_provider_id:
                user.oauth_provider_id = profile.provider_id
                user.auth_provider = profile.provider
            if profile.picture and not user.picture:
                user.picture = profile.picture

        await self.session.commit()
        await self.session.refresh(user)
        return self._to_entity(user, await self._resolve_roles(email))

    async def get(self, identity_id: str) -> AuthIdentity | None:
        try:
            pk = UUID(str(identity_id))
        except (ValueError, TypeError):
            return None
        user = await self.session.get(ExpertUserORM, pk)
        if user is None:
            return None
        return self._to_entity(user, await self._resolve_roles(user.email))

    @staticmethod
    def _to_entity(user: ExpertUserORM, roles: list[str]) -> AuthIdentity:
        return AuthIdentity(
            id=str(user.id),
            provider=user.auth_provider,
            provider_id=user.oauth_provider_id or "",
            email=user.email,
            name=user.name or "",
            roles=list(roles),
        )
