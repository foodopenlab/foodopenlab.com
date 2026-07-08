from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_user.adapter.outbound.pg.auth_pg_repository import AuthPgRepository
from mfds_user.app.ports.input.auth_use_case import AuthUseCase
from mfds_user.app.ports.output.auth_repository import AuthRepository
from mfds_user.app.use_cases.auth_interactor import AuthInteractor


def get_auth_repository(
    db: AsyncSession = Depends(get_db),
) -> AuthRepository:
    return AuthPgRepository(session=db)


def get_auth_use_case(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthUseCase:
    return AuthInteractor(auth_repository=repository)
