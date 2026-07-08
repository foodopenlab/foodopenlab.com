from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from titanic.adapter.outbound.repositories.crew_walter_roaster_repository import WalterRoasterRepository
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.use_cases.crew_walter_roaster_interactor import WalterRoasterInteractor


def get_walter_roaster_repository(
    db: AsyncSession = Depends(get_db),
) -> WalterRoasterRepository:
    return WalterRoasterRepository(session=db)


def get_walter_roaster_use_case(
    repository: WalterRoasterRepository = Depends(get_walter_roaster_repository),
) -> WalterRoasterUseCase:
    return WalterRoasterInteractor(repository=repository)
