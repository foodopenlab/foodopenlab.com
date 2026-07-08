from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from siliconvalley.adapter.outbound.client.piper_dinesh_dash_repository import DineshDashRepository
from siliconvalley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from siliconvalley.app.use_case.piper_dinesh_dash_interactor import DineshDashInteractor


def get_dinesh_repository(
    db: AsyncSession = Depends(get_db),
) -> DineshDashRepository:
    return DineshDashRepository(session=db)


def get_dinesh_use_case(
    repository: DineshDashRepository = Depends(get_dinesh_repository),
) -> DineshDashUseCase:
    return DineshDashInteractor(repository=repository)
