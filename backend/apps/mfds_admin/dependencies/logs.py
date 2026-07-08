from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_admin.adapter.outbound.pg.logs_pg_repository import LogsPgRepository
from mfds_admin.app.ports.input.logs_use_case import LogsUseCase
from mfds_admin.app.ports.output.logs_repository import LogsRepositoryPort
from mfds_admin.app.use_cases.logs_interactor import LogsInteractor


def get_logs_repository(
    db: AsyncSession = Depends(get_db),
) -> LogsRepositoryPort:
    return LogsPgRepository(session=db)


def get_logs_use_case(
    repository: LogsRepositoryPort = Depends(get_logs_repository),
) -> LogsUseCase:
    return LogsInteractor(repo=repository)
