from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.pg.anonymous_pg_repository import AnonymousPgRepository
from mfds_user.app.ports.output.anonymous_repository import AnonymousRepository


def get_anonymous_repository(
    db: AsyncSession = Depends(get_db),
) -> AnonymousRepository:
    return AnonymousPgRepository(session=db)
