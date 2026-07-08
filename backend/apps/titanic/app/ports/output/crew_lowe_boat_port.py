from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse


class LoweBoatPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: LoweBoatQuery) -> LoweBoatResponse:
        '''로우 구명보트의 자기 소개 레포지토리 추상 메소드'''
        pass
