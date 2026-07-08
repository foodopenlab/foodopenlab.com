from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse


class DunnCooUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: DunnCooQuery) -> DunnCooResponse:
        """COO — 자기소개"""
        pass
