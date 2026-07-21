from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse


class BighettiHrUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self) -> BighettiHrResponse:
        """BighettiHr — 자기소개 (정체성은 도메인 registry가 소유)"""
        pass
