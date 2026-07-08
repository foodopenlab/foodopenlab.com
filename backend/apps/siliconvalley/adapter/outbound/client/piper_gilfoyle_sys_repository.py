from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from siliconvalley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse
from siliconvalley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort

logger = logging.getLogger(__name__)


class GilfoyleSysRepository(GilfoyleSysPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: GilfoyleSysQuery) -> GilfoyleSysResponse:
        logger.info(f"[GilfoyleSysRepository] introduce_myself | query={query}")
        return GilfoyleSysResponse(id=query.id, name=query.name)
