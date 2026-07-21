from __future__ import annotations

from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrResponse
from siliconvalley.app.ports.input.piper_bighetti_hr_use_case import BighettiHrUseCase
from siliconvalley.domain.piper_crew_registry import get_crew_member
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


class BighettiHrInteractor(BighettiHrUseCase):

    _ROLE = PiperRole.HR

    async def introduce_myself(self) -> BighettiHrResponse:
        member = get_crew_member(self._ROLE)
        return BighettiHrResponse(id=member.id, name=member.name)
