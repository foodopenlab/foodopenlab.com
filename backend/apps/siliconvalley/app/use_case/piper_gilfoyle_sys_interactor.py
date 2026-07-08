from __future__ import annotations

from siliconvalley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysQuery, GilfoyleSysResponse
from siliconvalley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from siliconvalley.app.ports.output.piper_gilfoyle_sys_port import GilfoyleSysPort


class GilfoyleSysInteractor(GilfoyleSysUseCase):

    def __init__(self, repository: GilfoyleSysPort) -> None:
        self._repository = repository

    async def introduce_myself(self, query: GilfoyleSysQuery) -> GilfoyleSysResponse:
        return await self._repository.introduce_myself(query)
