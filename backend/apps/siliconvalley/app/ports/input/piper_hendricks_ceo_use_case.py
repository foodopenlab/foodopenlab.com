from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoResponse


class HendricksCeoUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self) -> HendricksCeoResponse:
        """HendricksCeo — 자기소개 (정체성은 도메인 registry가 소유)"""
        pass
