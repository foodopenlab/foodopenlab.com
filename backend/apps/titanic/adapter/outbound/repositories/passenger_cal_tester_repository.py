
from __future__ import annotations
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse

logger = logging.getLogger(__name__)

class CalTesterRepository:

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session

    async def introduce_myself(self, query: CalTesterQuery) -> CalTesterResponse:

        '''칼 테스터의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[CalTesterRepository] introduce_myself 진입 | request_data={query}")

        response: CalTesterResponse = CalTesterResponse(
            id= query.id * 10000,
            name= query.name + "가 레포지토리에 다녀옴"
        )
        return response
