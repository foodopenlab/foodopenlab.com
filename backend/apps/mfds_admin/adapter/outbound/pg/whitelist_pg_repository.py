from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_admin.app.ports.output.whitelist_repository import WhitelistRepositoryPort
from mfds_admin.adapter.outbound.orm.expert_whitelist_orm import ExpertWhitelistORM

class WhitelistPgRepository(WhitelistRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_email(self, email: str) -> Optional[ExpertWhitelistORM]:
        stmt = select(ExpertWhitelistORM).where(ExpertWhitelistORM.email == email.strip())
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()

    async def save(self, entry: ExpertWhitelistORM) -> ExpertWhitelistORM:
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def list_all(self) -> List[ExpertWhitelistORM]:
        stmt = select(ExpertWhitelistORM).order_by(ExpertWhitelistORM.added_at.desc())
        res = await self.session.execute(stmt)
        return list(res.scalars().all())

    async def delete_by_email(self, email: str) -> bool:
        entry = await self.get_by_email(email)
        if not entry:
            return False
        await self.session.delete(entry)
        await self.session.commit()
        return True
