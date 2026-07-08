
from __future__ import annotations
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse

logger = logging.getLogger(__name__)


class RoseModelRepository:

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def introduce_myself(self, query: RoseModelQuery) -> RoseModelResponse:

        '''로즈 모델의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[RoseModelRepository] introduce_myself 진입 | request_data={query}")

        response: RoseModelResponse = RoseModelResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
