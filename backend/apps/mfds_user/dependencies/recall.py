from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.cache.recall_cache_adapter import RecallCacheAdapter
from mfds_user.adapter.outbound.pg.recall_pg_repository import RecallPgRepository
from mfds_user.app.ports.input.recall_use_case import RecallUseCase
from mfds_user.app.ports.output.recall_cache_port import RecallCachePort
from mfds_user.app.ports.output.recall_repository import RecallRepositoryPort
from mfds_user.app.use_cases.recall_interactor import RecallInteractor


def get_recall_repository(
    db: AsyncSession = Depends(get_db),
) -> RecallRepositoryPort:
    return RecallPgRepository(session=db)


def get_recall_cache_port() -> RecallCachePort:
    return RecallCacheAdapter()


def get_recall_use_case(
    repository: RecallRepositoryPort = Depends(get_recall_repository),
    cache_port: RecallCachePort = Depends(get_recall_cache_port),
) -> RecallUseCase:
    return RecallInteractor(recall_repository=repository, cache_port=cache_port)
