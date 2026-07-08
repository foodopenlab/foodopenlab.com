from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from titanic.adapter.outbound.repositories.passenger_isidor_couple_repository import IsidorCoupleRepository
from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorCoupleUseCase
from titanic.app.use_cases.passenger_isidor_couple_interactor import IsidorCoupleInteractor


def get_isidor_couple_repository(
    db: AsyncSession = Depends(get_db),
) -> IsidorCoupleRepository:
    return IsidorCoupleRepository(session=db)


def get_isidor_couple_use_case(
    repository: IsidorCoupleRepository = Depends(get_isidor_couple_repository),
) -> IsidorCoupleUseCase:
    return IsidorCoupleInteractor(repository=repository)
