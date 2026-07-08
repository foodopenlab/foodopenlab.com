from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from braindead.adapter.outbound.repositories.contact_repository import ContactRepository
from braindead.app.ports.input.contact_use_case import IContactUseCase
from braindead.app.use_cases.contact_interactor import ContactInteractor
from matrix.grid_oracle_database_manager import get_db


def get_contact_use_case(db: AsyncSession = Depends(get_db)) -> IContactUseCase:
    return ContactInteractor(port=ContactRepository(session=db))
