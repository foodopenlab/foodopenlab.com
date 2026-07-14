from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db

from mfds_user.adapter.outbound.pg.law_chunk_pg_repository import LawChunkPgRepository
from mfds_user.app.ports.input.law_chunk_use_case import LawChunkSearchUseCase
from mfds_user.app.use_cases.law_chunk_interactor import LawChunkInteractor


def get_law_chunk_search_use_case(
    db: AsyncSession = Depends(get_db),
) -> LawChunkSearchUseCase:
    return LawChunkInteractor(repo=LawChunkPgRepository(db))
