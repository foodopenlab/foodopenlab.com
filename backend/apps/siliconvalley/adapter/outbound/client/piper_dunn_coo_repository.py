from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from siliconvalley.app.ports.output.piper_dunn_coo_port import DunnCooPort

logger = logging.getLogger(__name__)


class DunnCooRepository(DunnCooPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: DunnCooQuery) -> DunnCooResponse:
        logger.info(f"[DunnCooRepository] introduce_myself | query={query}")
        return DunnCooResponse(id=query.id, name=query.name)
