from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.orm.expert_whitelist_orm import ExpertWhitelistORM
from matrix.orm.expert_user_orm import ExpertUserORM
from mfds_user.app.dtos.oauth_dto import OAuthProfile
from mfds_user.app.ports.output.oauth_user_repository import OAuthUserRepository
from mfds_user.domain.entities.user_entity import User
from mfds_user.domain.value_objects.user_role_vo import UserRole


class OAuthUserPgRepository(OAuthUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def upsert_social_user(self, profile: OAuthProfile) -> User:
        # 이메일이 없으면(카카오 미검수 등) NOT NULL·unique 제약을 위해 합성 이메일 사용.
        email = profile.email or f"{profile.provider}_{profile.provider_id}@social.foodopenlab.local"

        # 1) (provider, provider_id)로 조회
        user = (
            await self.session.execute(
                select(ExpertUserORM).where(
                    ExpertUserORM.auth_provider == profile.provider,
                    ExpertUserORM.oauth_provider_id == profile.provider_id,
                )
            )
        ).scalar_one_or_none()

        # 2) 없으면 이메일로 조회(기존 계정 연결)
        if user is None:
            user = (
                await self.session.execute(
                    select(ExpertUserORM).where(ExpertUserORM.email == email)
                )
            ).scalar_one_or_none()

        now = datetime.utcnow()
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

        # 역할은 화이트리스트 승격 여부로 결정 (이메일 로그인과 동일 규칙).
        promoted = (
            await self.session.execute(
                select(ExpertWhitelistORM.email).where(ExpertWhitelistORM.email == user.email)
            )
        ).scalar_one_or_none()
        role = UserRole.EXPERT if promoted else UserRole.GENERAL

        return User(
            id=user.id,
            email=user.email,
            name=user.name,
            picture=user.picture,
            role=role,
            created_at=user.created_at,
            last_login=user.last_login,
        )
