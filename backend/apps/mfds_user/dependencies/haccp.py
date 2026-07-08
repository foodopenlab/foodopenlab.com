from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.pg.haccp_pg_repository import HaccpPgRepository
from mfds_user.app.ports.input.haccp_use_case import HaccpUseCase
from mfds_user.app.ports.output.haccp_repository import HaccpRepositoryPort
from mfds_user.app.use_cases.haccp_interactor import HaccpInteractor


def get_haccp_repository(
    db: AsyncSession = Depends(get_db),
) -> HaccpRepositoryPort:
    return HaccpPgRepository(session=db)


def get_haccp_use_case(
    repository: HaccpRepositoryPort = Depends(get_haccp_repository),
) -> HaccpUseCase:
    return HaccpInteractor(haccp_repository=repository)
