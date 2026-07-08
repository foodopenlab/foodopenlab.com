from typing import Optional
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.anonymous_repository import AnonymousRepository
from mfds_user.app.dtos.anonymous_dto import AnonymousDTO
from mfds_user.adapter.outbound.orm.anonymous_orm import AnonymousORM

class AnonymousPgRepository(AnonymousRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_by_cookie_id(self, cookie_id: str) -> Optional[AnonymousDTO]:
        query = select(AnonymousORM).where(AnonymousORM.cookie_id == cookie_id)
        result = await self.session.execute(query)
        db_anon = result.scalar_one_or_none()
        if db_anon:
            return AnonymousDTO(
                id=db_anon.id,
                cookie_id=db_anon.cookie_id,
                created_at=db_anon.created_at,
                last_seen=db_anon.last_seen
            )
        return None

    async def create_anonymous(self, cookie_id: str) -> AnonymousDTO:
        db_anon = AnonymousORM(
            cookie_id=cookie_id,
            created_at=datetime.utcnow(),
            last_seen=datetime.utcnow()
        )
        self.session.add(db_anon)
        await self.session.commit()
        await self.session.refresh(db_anon)
        return AnonymousDTO(
            id=db_anon.id,
            cookie_id=db_anon.cookie_id,
            created_at=db_anon.created_at,
            last_seen=db_anon.last_seen
        )

    async def update_last_seen(self, cookie_id: str) -> AnonymousDTO:
        now = datetime.utcnow()
        query = select(AnonymousORM).where(AnonymousORM.cookie_id == cookie_id)
        result = await self.session.execute(query)
        db_anon = result.scalar_one()
        db_anon.last_seen = now
        await self.session.commit()
        await self.session.refresh(db_anon)
        return AnonymousDTO(
            id=db_anon.id,
            cookie_id=db_anon.cookie_id,
            created_at=db_anon.created_at,
            last_seen=db_anon.last_seen
        )
