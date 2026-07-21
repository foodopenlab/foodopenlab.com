from __future__ import annotations

from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashResponse
from siliconvalley.app.ports.input.piper_dinesh_dash_use_case import DineshDashUseCase
from siliconvalley.domain.piper_crew_registry import get_crew_member
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


class DineshDashInteractor(DineshDashUseCase):

    _ROLE = PiperRole.DASH

    async def introduce_myself(self) -> DineshDashResponse:
        member = get_crew_member(self._ROLE)
        return DineshDashResponse(id=member.id, name=member.name)
