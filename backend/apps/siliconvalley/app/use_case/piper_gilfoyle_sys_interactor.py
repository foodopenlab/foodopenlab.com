from __future__ import annotations

from siliconvalley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysResponse
from siliconvalley.app.ports.input.piper_gilfoyle_sys_use_case import GilfoyleSysUseCase
from siliconvalley.domain.piper_crew_registry import get_crew_member
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


class GilfoyleSysInteractor(GilfoyleSysUseCase):

    _ROLE = PiperRole.SYS

    async def introduce_myself(self) -> GilfoyleSysResponse:
        member = get_crew_member(self._ROLE)
        return GilfoyleSysResponse(id=member.id, name=member.name)
