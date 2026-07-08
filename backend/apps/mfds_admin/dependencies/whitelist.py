from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_admin.adapter.outbound.pg.whitelist_pg_repository import WhitelistPgRepository
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.app.ports.output.whitelist_repository import WhitelistRepositoryPort
from mfds_admin.app.use_cases.whitelist_interactor import WhitelistInteractor


def get_whitelist_repository(
    db: AsyncSession = Depends(get_db),
) -> WhitelistRepositoryPort:
    return WhitelistPgRepository(session=db)


def get_whitelist_use_case(
    repository: WhitelistRepositoryPort = Depends(get_whitelist_repository),
) -> WhitelistUseCase:
    return WhitelistInteractor(whitelist_repository=repository)
