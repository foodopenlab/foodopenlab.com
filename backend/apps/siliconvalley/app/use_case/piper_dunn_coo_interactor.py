from __future__ import annotations

from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooQuery, DunnCooResponse
from siliconvalley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from siliconvalley.app.ports.output.piper_dunn_coo_port import DunnCooPort


class DunnCooInteractor(DunnCooUseCase):

    def __init__(self, repository: DunnCooPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: DunnCooQuery) -> DunnCooResponse:
        return await self._repository.introduce_myself(query)
