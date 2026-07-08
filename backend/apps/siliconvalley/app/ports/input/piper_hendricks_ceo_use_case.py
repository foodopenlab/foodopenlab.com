from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoQuery, HendricksCeoResponse


class HendricksCeoUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: HendricksCeoQuery) -> HendricksCeoResponse:
        """CEO — 자기소개"""
        pass
