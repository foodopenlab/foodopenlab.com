from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from titanic.adapter.outbound.repositories.crew_hartley_violin_repository import HartleyViolinRepository
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.app.use_cases.crew_hartley_violin_interactor import HartleyViolinInteractor
from titanic.dependencies.crew_walter_roaster_provider import get_walter_roaster_use_case


def get_hartley_violin_repository(
    db: AsyncSession = Depends(get_db),
) -> HartleyViolinRepository:
    return HartleyViolinRepository(session=db)


def get_hartley_violin_use_case(
    repository: HartleyViolinRepository = Depends(get_hartley_violin_repository),
    walter: WalterRoasterUseCase = Depends(get_walter_roaster_use_case),
) -> HartleyViolinUseCase:
    return HartleyViolinInteractor(repository=repository, walter=walter)
