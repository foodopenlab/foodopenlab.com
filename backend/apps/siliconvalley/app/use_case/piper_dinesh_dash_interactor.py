from __future__ import annotations

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse
from siliconvalley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from siliconvalley.app.ports.output.piper_dinesh_dash_port import DineshDashPort


class DineshDashInteractor(DineshDashUseCase):

    def __init__(self, repository: DineshDashPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: DineshDashQuery) -> DineshDashResponse:
        return await self._repository.introduce_myself(query)
