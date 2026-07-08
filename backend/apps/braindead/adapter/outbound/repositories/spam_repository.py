from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.mappers.spam_orm_mapper import SpamOrmMapper
from braindead.adapter.outbound.orm.spam_orm import SpamLogORM
from braindead.app.dtos.spam_dto import SpamResultDTO
from braindead.app.ports.output.spam_port import ISpamPort
from braindead.domain.entities.spam_entity import SpamEntity


class SpamRepository(ISpamPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, entity: SpamEntity) -> SpamResultDTO:
        orm = SpamOrmMapper.to_orm(entity)
        self._session.add(orm)
        await self._session.commit()
        await self._session.refresh(orm)
        return SpamOrmMapper.to_dto(orm)

    async def find_all(self) -> list[SpamResultDTO]:
        result = await self._session.execute(
            select(SpamLogORM).order_by(SpamLogORM.id.desc())
        )
        return [SpamOrmMapper.to_dto(row) for row in result.scalars().all()]
