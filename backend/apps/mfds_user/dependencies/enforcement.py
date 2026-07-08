from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.cache.enforcement_cache_adapter import EnforcementCacheAdapter
from mfds_user.adapter.outbound.pg.enforcement_pg_repository import EnforcementPgRepository
from mfds_user.app.ports.input.enforcement_use_case import EnforcementUseCase
from mfds_user.app.ports.output.enforcement_cache_port import EnforcementCachePort
from mfds_user.app.ports.output.enforcement_repository import EnforcementRepositoryPort
from mfds_user.app.use_cases.enforcement_interactor import EnforcementInteractor


def get_enforcement_repository(
    db: AsyncSession = Depends(get_db),
) -> EnforcementRepositoryPort:
    return EnforcementPgRepository(session=db)


def get_enforcement_cache_port() -> EnforcementCachePort:
    return EnforcementCacheAdapter()


def get_enforcement_use_case(
    repository: EnforcementRepositoryPort = Depends(get_enforcement_repository),
    cache_port: EnforcementCachePort = Depends(get_enforcement_cache_port),
) -> EnforcementUseCase:
    return EnforcementInteractor(enforcement_repository=repository, cache_port=cache_port)
