
from __future__ import annotations
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse

logger = logging.getLogger(__name__)

class HartleyViolinRepository:

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def introduce_myself(self, query: HartleyViolinQuery) -> HartleyViolinResponse:

        '''하틀리 바이올린의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[HartleyViolinRepository] introduce_myself 진입 | request_data={query}")

        response: HartleyViolinResponse = HartleyViolinResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
