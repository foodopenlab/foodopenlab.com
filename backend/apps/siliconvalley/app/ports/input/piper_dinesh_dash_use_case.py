from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashResponse


class DineshDashUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self) -> DineshDashResponse:
        """DineshDash — 자기소개 (정체성은 도메인 registry가 소유)"""
        pass
