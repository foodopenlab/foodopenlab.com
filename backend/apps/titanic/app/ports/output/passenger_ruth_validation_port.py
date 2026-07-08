from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationQuery, RuthValidationResponse


class RuthValidationPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: RuthValidationQuery) -> RuthValidationResponse:
        '''루스 밸리데이션의 자기 소개 레포지토리 추상 메소드'''
        pass
