"""Piper 크루 5인의 정체성 SSOT — 라우터 하드코딩을 대체하는 도메인 소유 데이터."""
from __future__ import annotations

from siliconvalley.domain.entities.piper_crew_member_entity import PiperCrewMember
from siliconvalley.domain.value_objects.piper_role_vo import PiperRole

_CREW: dict[PiperRole, PiperCrewMember] = {
    PiperRole.CEO: PiperCrewMember(id=5, name="헨드릭스 CEO (Hendricks CEO)", role=PiperRole.CEO),
    PiperRole.COO: PiperCrewMember(id=3, name="던 COO (Dunn COO)", role=PiperRole.COO),
    PiperRole.HR: PiperCrewMember(id=1, name="빅헤티 HR (Bighetti HR)", role=PiperRole.HR),
    PiperRole.SYS: PiperCrewMember(id=4, name="Gilfoyle Sys", role=PiperRole.SYS),
    PiperRole.DASH: PiperCrewMember(id=2, name="디네시 대시 (Dinesh Dash)", role=PiperRole.DASH),
}


def get_crew_member(role: PiperRole) -> PiperCrewMember:
    return _CREW[role]
