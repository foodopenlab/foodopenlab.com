from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.adapter.outbound.pg.auth_identity_orm import AuthIdentityORM
from auth.app.dtos.auth_dto import OAuthProfile
from auth.app.ports.output.identity_port import IIdentityPort
from auth.domain.entities.auth_identity_entity import AuthIdentity


class AuthIdentityRepository(IIdentityPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_oauth_identity(self, profile: OAuthProfile, roles: list[str]) -> AuthIdentity:
        email = profile.email or f"{profile.provider}_{profile.provider_id}@social.foodopenlab.local"
        orm = (
            await self.session.execute(
                select(AuthIdentityORM).where(
                    AuthIdentityORM.provider == profile.provider,
                    AuthIdentityORM.provider_id == profile.provider_id,
                )
            )
        ).scalar_one_or_none()

        if orm is None:
            orm = AuthIdentityORM(
                provider=profile.provider,
                provider_id=profile.provider_id,
                email=email,
                name=profile.name,
                roles=list(roles),
            )
            self.session.add(orm)
        else:
            orm.email = email
            orm.name = profile.name
            orm.roles = list(roles)  # 로그인마다 화이트리스트 재평가 반영
        await self.session.commit()
        await self.session.refresh(orm)
        return self._to_entity(orm)

    async def get(self, identity_id: str) -> AuthIdentity | None:
        try:
            pk = int(identity_id)
        except (TypeError, ValueError):
            return None
        orm = await self.session.get(AuthIdentityORM, pk)
        return self._to_entity(orm) if orm else None

    @staticmethod
    def _to_entity(orm: AuthIdentityORM) -> AuthIdentity:
        return AuthIdentity(
            id=orm.id,
            provider=orm.provider,
            provider_id=orm.provider_id,
            email=orm.email,
            name=orm.name,
            roles=list(orm.roles or []),
            created_at=orm.created_at,
        )
