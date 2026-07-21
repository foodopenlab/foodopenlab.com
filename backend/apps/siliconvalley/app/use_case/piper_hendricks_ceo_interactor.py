from __future__ import annotations

from siliconvalley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoResponse
from siliconvalley.app.ports.input.piper_hendricks_ceo_use_case import HendricksCeoUseCase
from siliconvalley.domain.piper_crew_registry import get_crew_member
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


class HendricksCeoInteractor(HendricksCeoUseCase):

    _ROLE = PiperRole.CEO

    async def introduce_myself(self) -> HendricksCeoResponse:
        member = get_crew_member(self._ROLE)
        return HendricksCeoResponse(id=member.id, name=member.name)
