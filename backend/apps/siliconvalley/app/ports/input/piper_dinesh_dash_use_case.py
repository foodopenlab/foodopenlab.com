from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


class DineshDashUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        """대시보드 담당 — 자기소개"""
        pass
