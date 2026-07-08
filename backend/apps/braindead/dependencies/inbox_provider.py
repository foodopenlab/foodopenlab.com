from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.repositories.inbox_repository import InboxRepository
from braindead.app.ports.input.inbox_use_case import IInboxUseCase
from braindead.app.use_cases.inbox_interactor import InboxInteractor
from matrix.grid_oracle_database_manager import get_db


def get_inbox_use_case(db: AsyncSession = Depends(get_db)) -> IInboxUseCase:
    return InboxInteractor(port=InboxRepository(session=db))
