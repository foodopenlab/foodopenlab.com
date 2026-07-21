from __future__ import annotations

from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooResponse
from siliconvalley.app.ports.input.piper_dunn_coo_use_case import DunnCooUseCase
from siliconvalley.domain.piper_crew_registry import get_crew_member
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


class DunnCooInteractor(DunnCooUseCase):

    _ROLE = PiperRole.COO

    async def introduce_myself(self) -> DunnCooResponse:
        member = get_crew_member(self._ROLE)
        return DunnCooResponse(id=member.id, name=member.name)
