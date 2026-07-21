from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooResponse


class DunnCooUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self) -> DunnCooResponse:
        """DunnCoo — 자기소개 (정체성은 도메인 registry가 소유)"""
        pass
