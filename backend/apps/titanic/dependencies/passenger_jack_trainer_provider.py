from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from titanic.adapter.outbound.ml.survival_strategies import build_all_strategies
from titanic.adapter.outbound.repositories.passenger_jack_trainer_repository import JackTrainerRepository
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.use_cases.passenger_jack_trainer_interactor import JackTrainerInteractor


def get_jack_trainer_repository(
    db: AsyncSession = Depends(get_db),
) -> JackTrainerRepository:
    return JackTrainerRepository(session=db)


def get_jack_trainer_use_case(
    repository: JackTrainerRepository = Depends(get_jack_trainer_repository),
) -> JackTrainerUseCase:
    return JackTrainerInteractor(repository=repository, build_strategies=build_all_strategies)
