from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterResponse


class CalTesterUseCase(ABC):

    @abstractmethod
    async def test_model(self, test_set: dict[str, Any]) -> dict[str, Any]:
        '''Jack이 훈련한 로즈 전략들을 채점해 챔피언·순위를 반환하는 메소드'''
        pass

    @abstractmethod
    async def introduce_myself(self, schema: CalTesterSchema) -> CalTesterResponse:
        '''칼 테스터의 자기소개 메소드'''
        pass
