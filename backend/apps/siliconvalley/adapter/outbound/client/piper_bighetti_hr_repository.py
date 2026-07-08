from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse
from siliconvalley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort

logger = logging.getLogger(__name__)


class BighettiHrRepository(BighettiHrPort):

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        logger.info(f"[BighettiHrRepository] introduce_myself | query={query}")
        return BighettiHrResponse(id=query.id, name=query.name)
