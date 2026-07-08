from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from mfds_admin.adapter.outbound.pg.admin_pg_repository import AdminPgRepository
from mfds_admin.app.ports.input.admin_auth_use_case import AdminAuthUseCase
from mfds_admin.app.ports.output.admin_repository import AdminRepositoryPort
from mfds_admin.app.use_cases.admin_auth_interactor import AdminAuthInteractor


def get_admin_repository(
    db: AsyncSession = Depends(get_db),
) -> AdminRepositoryPort:
    return AdminPgRepository(session=db)


def get_admin_auth_use_case(
    repository: AdminRepositoryPort = Depends(get_admin_repository),
) -> AdminAuthUseCase:
    return AdminAuthInteractor(admin_repository=repository)
