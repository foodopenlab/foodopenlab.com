
from __future__ import annotations
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationQuery, RuthValidationResponse

logger = logging.getLogger(__name__)

class RuthValidationRepository:

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def introduce_myself(self, query: RuthValidationQuery) -> RuthValidationResponse:

        '''루스 밸리데이션의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[RuthValidationRepository] introduce_myself 진입 | request_data={query}")

        response: RuthValidationResponse = RuthValidationResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
