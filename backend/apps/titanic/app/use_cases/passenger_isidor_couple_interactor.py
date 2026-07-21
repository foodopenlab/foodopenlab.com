from __future__ import annotations

from titanic.app.dtos.passenger_isidor_couple_dto import IsidorCoupleQuery, IsidorCoupleResponse
from titanic.app.ports.input.passenger_isidor_couple_use_case import IsidorCoupleUseCase


class IsidorCoupleInteractor(IsidorCoupleUseCase):

    def __init__(self, repository):
        self.repository = repository

    async def introduce_myself(self, query: IsidorCoupleQuery) -> IsidorCoupleResponse:
        '''이시도르 커플의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(query)
