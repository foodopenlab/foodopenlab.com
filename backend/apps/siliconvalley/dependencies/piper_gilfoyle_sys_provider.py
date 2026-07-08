from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from siliconvalley.adapter.outbound.client.piper_gilfoyle_sys_repository import GilfoyleSysRepository
from siliconvalley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from siliconvalley.app.use_case.piper_gilfoyle_sys_interactor import GilfoyleSysInteractor


def get_gilfoyle_repository(
    db: AsyncSession = Depends(get_db),
) -> GilfoyleSysRepository:
    return GilfoyleSysRepository(session=db)


def get_gilfoyle_use_case(
    repository: GilfoyleSysRepository = Depends(get_gilfoyle_repository),
) -> GilfoyleSysUseCase:
    return GilfoyleSysInteractor(repository=repository)
