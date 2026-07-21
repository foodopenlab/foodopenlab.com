from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse


class HartleyViolinUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: HartleyViolinQuery) -> HartleyViolinResponse:
        '''하틀리 바이올린의 자기소개 메소드'''

    @abstractmethod
    async def get_correlation_heatmap(self) -> bytes:
        '''train set 변수 간 상관관계 히트맵 PNG 바이트'''
