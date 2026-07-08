from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_oracle_database_manager import get_db
from siliconvalley.adapter.outbound.client.piper_hendricks_ceo_repository import HendricksCeoRepository
from siliconvalley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from siliconvalley.app.use_case.piper_hendricks_ceo_interactor import HendricksCeoInteractor


def get_hendricks_repository(
    db: AsyncSession = Depends(get_db),
) -> HendricksCeoRepository:
    return HendricksCeoRepository(session=db)


def get_hendricks_use_case(
    repository: HendricksCeoRepository = Depends(get_hendricks_repository),
) -> HendricksCeoUseCase:
    return HendricksCeoInteractor(repository=repository)
