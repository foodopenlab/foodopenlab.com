from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_admin.app.ports.output.whitelist_repository import WhitelistRepositoryPort
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand, WhitelistEntryDTO
from matrix.orm.expert_whitelist_orm import ExpertWhitelistORM

class WhitelistPgRepository(WhitelistRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_dto(self, row: ExpertWhitelistORM) -> WhitelistEntryDTO:
        return WhitelistEntryDTO(
            email=row.email,
            invited_name=row.invited_name,
            role_desc=row.role_desc,
            added_by=row.added_by,
            added_at=row.added_at,
        )

    async def get_by_email(self, email: str) -> Optional[WhitelistEntryDTO]:
        stmt = select(ExpertWhitelistORM).where(ExpertWhitelistORM.email == email.strip())
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()
        return self._to_dto(row) if row else None

    async def save(self, command: AddWhitelistCommand) -> WhitelistEntryDTO:
        row = ExpertWhitelistORM(
            email=command.email.strip(),
            invited_name=command.invited_name,
            role_desc=command.role_desc,
            added_by=command.added_by,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return self._to_dto(row)

    async def list_all(self) -> List[WhitelistEntryDTO]:
        stmt = select(ExpertWhitelistORM).order_by(ExpertWhitelistORM.added_at.desc())
        res = await self.session.execute(stmt)
        return [self._to_dto(row) for row in res.scalars().all()]

    async def delete_by_email(self, email: str) -> bool:
        stmt = select(ExpertWhitelistORM).where(ExpertWhitelistORM.email == email.strip())
        res = await self.session.execute(stmt)
        row = res.scalar_one_or_none()
        if not row:
            return False
        await self.session.delete(row)
        await self.session.commit()
        return True
