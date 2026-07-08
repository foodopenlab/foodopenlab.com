from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from siliconvalley.adapter.outbound.client.piper_dunn_coo_repository import DunnCooRepository
from siliconvalley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from siliconvalley.app.use_case.piper_dunn_coo_interactor import DunnCooInteractor


def get_dunn_repository(
    db: AsyncSession = Depends(get_db),
) -> DunnCooRepository:
    return DunnCooRepository(session=db)


def get_dunn_use_case(
    repository: DunnCooRepository = Depends(get_dunn_repository),
) -> DunnCooUseCase:
    return DunnCooInteractor(repository=repository)
