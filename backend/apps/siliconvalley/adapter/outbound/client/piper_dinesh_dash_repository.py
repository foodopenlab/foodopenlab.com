from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse
from siliconvalley.app.ports.output.piper_dinesh_dash_port import DineshDashPort

logger = logging.getLogger(__name__)


class DineshDashRepository(DineshDashPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        logger.info(f"[DineshDashRepository] introduce_myself | query={query}")
        return DineshDashResponse(id=query.id, name=query.name)
