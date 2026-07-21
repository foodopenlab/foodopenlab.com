from __future__ import annotations

from titanic.app.dtos.passenger_molly_scaler_dto import MollyScalerQuery, MollyScalerResponse
from titanic.app.ports.input.passenger_molly_scaler_use_case import MollyScalerUseCase


class MollyScalerInteractor(MollyScalerUseCase):

    def __init__(self, repository):
        self.repository = repository

    async def introduce_myself(self, query: MollyScalerQuery) -> MollyScalerResponse:
        '''몰리 스케일러의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(query)
