from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.pg.industry_pg_repository import IndustryPgRepository
from mfds_user.app.ports.input.industry_use_case import IndustryUseCase
from mfds_user.app.ports.output.industry_repository import IndustryRepository
from mfds_user.app.use_cases.industry_interactor import IndustryInteractor


def get_industry_repository(
    db: AsyncSession = Depends(get_db),
) -> IndustryRepository:
    return IndustryPgRepository(session=db)


def get_industry_use_case(
    repository: IndustryRepository = Depends(get_industry_repository),
) -> IndustryUseCase:
    return IndustryInteractor(repo=repository)
