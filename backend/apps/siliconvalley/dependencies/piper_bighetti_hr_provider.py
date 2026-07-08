from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from siliconvalley.adapter.outbound.client.piper_bighetti_hr_repository import BighettiHrRepository
from siliconvalley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from siliconvalley.app.use_case.piper_bighetti_hr_interactor import BighettiHrInteractor


def get_bighetti_repository(
    db: AsyncSession = Depends(get_db),
) -> BighettiHrRepository:
    return BighettiHrRepository(session=db)


def get_bighetti_use_case(
    repository: BighettiHrRepository = Depends(get_bighetti_repository),
) -> BighettiHrUseCase:
    return BighettiHrInteractor(repository=repository)
