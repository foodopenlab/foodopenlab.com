from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


class DineshDashPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        """대시보드 담당 — outbound port"""
        pass
