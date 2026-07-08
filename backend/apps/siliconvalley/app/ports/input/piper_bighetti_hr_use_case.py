from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse


class BighettiHrUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        """HR 담당 — 자기소개"""
        pass
