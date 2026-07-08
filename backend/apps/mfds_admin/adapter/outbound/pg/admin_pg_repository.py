from typing import Optional
from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_admin.app.ports.output.admin_repository import AdminRepositoryPort
from mfds_admin.adapter.outbound.orm.admin_orm import AdminORM

class AdminPgRepository(AdminRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_admin_by_email(self, email: str) -> Optional[AdminORM]:
        stmt = select(AdminORM).where(AdminORM.email == email.strip())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def update_last_login(self, admin_id: UUID) -> None:
        row = await self.session.get(AdminORM, admin_id)
        if row:
            row.last_login = datetime.utcnow()
            self.session.add(row)
            await self.session.commit()
            await self.session.refresh(row)
