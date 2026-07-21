import secrets
from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from matrix.grid_cypher_password_manager import hash_password
from mfds_admin.app.ports.output.admin_repository import AdminRepositoryPort
from mfds_admin.adapter.outbound.orm.admin_orm import AdminORM
from mfds_admin.domain.entities.admin_entity import Admin

class AdminPgRepository(AdminRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_admin_by_email(self, email: str) -> Optional[Admin]:
        stmt = select(AdminORM).where(AdminORM.email == email.strip())
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()
        if row is None:
            return None
        return Admin(
            id=row.id,
            email=row.email,
            name=row.name,
            hashed_password=row.hashed_password,
            last_login=row.last_login,
        )

    async def update_last_login(self, admin_id: UUID) -> None:
        row = await self.session.get(AdminORM, admin_id)
        if row:
            row.last_login = datetime.utcnow()
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)

    async def upsert_google_admin(self, email: str, name: str) -> Admin:
        normalized = email.strip().lower()
        row = (
            await self.session.execute(select(AdminORM).where(AdminORM.email == normalized))
        ).scalar_one_or_none()
        if row is None:
            # 비밀번호 로그인은 폐지 — NOT NULL 제약 충족용 사용 불가 랜덤 해시.
            row = AdminORM(
                email=normalized,
                name=name or normalized,
                hashed_password=hash_password(secrets.token_hex(32)),
                last_login=datetime.utcnow(),
            )
            self.session.add(row)
        else:
            row.last_login = datetime.utcnow()
            if name and not row.name:
                row.name = name
        await self.session.commit()
        await self.session.refresh(row)
        return Admin(
            id=row.id,
            email=row.email,
            name=row.name,
            hashed_password=row.hashed_password,
            last_login=row.last_login,
        )
