from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse


class MollyScalerUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: MollyScalerQuery) -> MollyScalerResponse:
        '''몰리 스케일러의 자기소개 메소드'''
        pass
