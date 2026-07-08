from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from titanic.adapter.outbound.repositories.passenger_rose_model_repository import RoseModelRepository
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase
from titanic.app.use_cases.passenger_rose_model_interactor import RoseModelInteractor


def get_rose_model_repository(
    db: AsyncSession = Depends(get_db),
) -> RoseModelRepository:
    return RoseModelRepository(session=db)


def get_rose_model_use_case(
    repository: RoseModelRepository = Depends(get_rose_model_repository),
) -> RoseModelUseCase:
    return RoseModelInteractor(repository=repository)
