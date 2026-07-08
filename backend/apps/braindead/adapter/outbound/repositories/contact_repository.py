from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.mappers.contact_orm_mapper import ContactOrmMapper
from braindead.adapter.outbound.orm.contact_orm import ContactORM
from braindead.app.dtos.contact_dto import ContactDTO, UploadResultDTO
from braindead.app.ports.output.contact_port import IContactPort
from braindead.domain.entities.contact_entity import ContactEntity


class ContactRepository(IContactPort):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_all(self, contacts: list[ContactEntity]) -> UploadResultDTO:
        existing_emails = await self._fetch_existing_emails()
        existing_names = await self._fetch_existing_names()

        new_contacts = [
            c for c in contacts
            if (c.email and c.email not in existing_emails)
            or (not c.email and c.name and c.name not in existing_names)
        ]

        if not new_contacts:
            return UploadResultDTO(count=0)

        self._session.add_all([ContactOrmMapper.to_orm(c) for c in new_contacts])
        await self._session.commit()
        return UploadResultDTO(count=len(new_contacts))

    async def find_all(self) -> list[ContactDTO]:
        result = await self._session.execute(select(ContactORM).order_by(ContactORM.id))
        return [ContactOrmMapper.to_dto(row) for row in result.scalars().all()]

    async def search(self, query: str) -> list[ContactDTO]:
        like = f"%{query}%"
        result = await self._session.execute(
            select(ContactORM)
            .where(or_(ContactORM.name.ilike(like), ContactORM.email.ilike(like)))
            .order_by(ContactORM.name)
            .limit(10)
        )
        return [ContactOrmMapper.to_dto(row) for row in result.scalars().all()]

    async def _fetch_existing_emails(self) -> set[str]:
        result = await self._session.execute(
            select(ContactORM.email).where(ContactORM.email.isnot(None))
        )
        return {row[0] for row in result}

    async def _fetch_existing_names(self) -> set[str]:
        result = await self._session.execute(
            select(ContactORM.name).where(ContactORM.name.isnot(None))
        )
        return {row[0] for row in result}
