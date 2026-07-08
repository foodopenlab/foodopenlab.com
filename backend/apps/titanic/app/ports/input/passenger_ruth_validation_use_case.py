from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_ruth_validation_schema import RuthValidationSchema
from titanic.app.dtos.passenger_ruth_validation_dto import RuthValidationResponse


class RuthValidationUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, schema: RuthValidationSchema) -> RuthValidationResponse:
        '''루스 밸리데이션의 자기소개 메소드'''
        pass
