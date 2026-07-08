from __future__ import annotations

from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse
from siliconvalley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from siliconvalley.app.ports.output.piper_bighetti_hr_port import BighettiHrPort


class BighettiHrInteractor(BighettiHrUseCase):

    def __init__(self, repository: BighettiHrPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: BighettiHrQuery) -> BighettiHrResponse:
        return await self._repository.introduce_myself(query)
