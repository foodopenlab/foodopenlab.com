from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationQuery, RuthValidationResponse


class RuthValidationUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: RuthValidationQuery) -> RuthValidationResponse:
        '''루스 밸리데이션의 자기소개 메소드'''
        pass
