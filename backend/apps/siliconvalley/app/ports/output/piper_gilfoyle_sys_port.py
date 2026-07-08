from __future__ import annotations

from abc import ABC, abstractmethod

from siliconvalley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse


class GilfoyleSysPort(ABC):

    @abstractmethod
    async def introduce_myself(self, query: GilfoyleSysQuery) -> GilfoyleSysResponse:
        """시스템 담당 — outbound port"""
        pass
