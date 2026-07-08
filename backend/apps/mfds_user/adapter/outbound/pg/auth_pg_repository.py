from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.domain.entities.user_entity import User
from mfds_user.domain.value_objects.user_role_vo import UserRole
from mfds_user.app.dtos.auth_dto import UserSessionDTO
from mfds_user.adapter.outbound.orm.expert_user_orm import ExpertUserORM
from mfds_user.adapter.outbound.orm.expert_user_session_orm import ExpertUserSessionORM
from mfds_admin.adapter.outbound.orm.expert_whitelist_orm import ExpertWhitelistORM

class AuthPgRepository(AuthRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_whitelisted_email(self, email: str) -> Optional[dict]:
        query = select(ExpertWhitelistORM).where(ExpertWhitelistORM.email == email)
        result = await self.session.execute(query)
        entry = result.scalar_one_or_none()
        if entry:
            return {
                "email": entry.email,
                "invited_name": entry.invited_name,
                "role_desc": entry.role_desc
            }
        return None

    async def find_user_by_email(self, email: str) -> Optional[User]:
        query = select(ExpertUserORM).where(ExpertUserORM.email == email)
        result = await self.session.execute(query)
        db_user = result.scalar_one_or_none()
        if db_user:
            return User(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name,
                picture=db_user.picture,
                role=UserRole.EXPERT,  # v9의 모든 일반/전문 가입자는 expert
                created_at=db_user.created_at,
                last_login=db_user.last_login
            )
        return None

    async def get_hashed_password(self, email: str) -> Optional[str]:
        query = select(ExpertUserORM.hashed_password).where(ExpertUserORM.email == email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def save_user(self, email: str, name: str, password_hash: str, agreed: bool, role: str) -> User:
        db_user = ExpertUserORM(
            email=email,
            name=name,
            hashed_password=password_hash,
            auth_provider="email"
        )
        self.session.add(db_user)
        await self.session.commit()
        await self.session.refresh(db_user)
        return User(
            id=db_user.id,
            email=db_user.email,
            name=db_user.name,
            picture=db_user.picture,
            role=UserRole.EXPERT,
            created_at=db_user.created_at,
            last_login=db_user.last_login
        )

    async def save_session(self, session: UserSessionDTO) -> None:
        db_session = ExpertUserSessionORM(
            expert_user_id=session.user_id,
            access_token=session.access_token,
            refresh_token=session.refresh_token,
            expires_at=session.expires_at
        )
        self.session.add(db_session)
        await self.session.commit()

    async def find_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSessionDTO]:
        query = select(ExpertUserSessionORM, ExpertUserORM).join(
            ExpertUserORM, ExpertUserSessionORM.expert_user_id == ExpertUserORM.id
        ).where(ExpertUserSessionORM.refresh_token == refresh_token)
        result = await self.session.execute(query)
        row = result.first()
        if row:
            db_session, db_user = row
            return UserSessionDTO(
                user_id=db_user.id,
                email=db_user.email,
                name=db_user.name or "",
                role="expert",
                access_token=db_session.access_token,
                refresh_token=db_session.refresh_token,
                expires_at=db_session.expires_at
            )
        return None

    async def delete_session_by_access_token(self, access_token: str) -> None:
        stmt = delete(ExpertUserSessionORM).where(ExpertUserSessionORM.access_token == access_token)
        await self.session.execute(stmt)
        await self.session.commit()

    async def update_last_login(self, user_id: UUID) -> None:
        stmt = update(ExpertUserORM).where(ExpertUserORM.id == user_id).values(
            last_login=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def find_all_active(self) -> list[User]:
        query = select(ExpertUserORM)
        result = await self.session.execute(query)
        db_users = result.scalars().all()
        return [
            User(
                id=db_user.id,
                email=db_user.email,
                name=db_user.name,
                picture=db_user.picture,
                role=UserRole.EXPERT,
                created_at=db_user.created_at,
                last_login=db_user.last_login
            )
            for db_user in db_users
        ]
