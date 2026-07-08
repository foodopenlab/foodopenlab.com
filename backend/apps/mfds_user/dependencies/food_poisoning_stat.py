from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.pg.food_poisoning_stat_pg_repository import (
    FoodPoisoningStatPgRepository,
)
from mfds_user.app.ports.input.food_poisoning_stat_use_case import FoodPoisoningStatUseCase
from mfds_user.app.ports.output.food_poisoning_stat_repository import (
    FoodPoisoningStatRepositoryPort,
)
from mfds_user.app.use_cases.food_poisoning_stat_interactor import FoodPoisoningStatInteractor


def get_food_poisoning_stat_repository(
    db: AsyncSession = Depends(get_db),
) -> FoodPoisoningStatRepositoryPort:
    return FoodPoisoningStatPgRepository(session=db)


def get_food_poisoning_stat_use_case(
    repository: FoodPoisoningStatRepositoryPort = Depends(get_food_poisoning_stat_repository),
) -> FoodPoisoningStatUseCase:
    return FoodPoisoningStatInteractor(repository=repository)
