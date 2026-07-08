from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.mappers.inbox_orm_mapper import InboxOrmMapper
from braindead.adapter.outbound.orm.inbox_orm import InboxEmailORM
from braindead.app.dtos.inbox_dto import InboxEmailDTO
from braindead.app.ports.output.inbox_port import IInboxPort
from braindead.domain.entities.inbox_entity import InboxEmailEntity


class InboxRepository(IInboxPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, entity: InboxEmailEntity) -> InboxEmailDTO:
        if entity.gmail_message_id:
            existing = await self._find_by_gmail_message_id(entity.gmail_message_id)
            if existing is not None:
                return InboxOrmMapper.to_dto(existing)

        orm = InboxOrmMapper.to_orm(entity)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return InboxOrmMapper.to_dto(orm)

    async def find_all(self) -> list[InboxEmailDTO]:
        result = await self._session.execute(select(InboxEmailORM).order_by(InboxEmailORM.id.desc()))
        return [InboxOrmMapper.to_dto(row) for row in result.scalars().all()]

    async def _find_by_gmail_message_id(self, gmail_message_id: str) -> InboxEmailORM | None:
        result = await self._session.execute(
            select(InboxEmailORM).where(InboxEmailORM.gmail_message_id == gmail_message_id)
        )
        return result.scalars().first()
