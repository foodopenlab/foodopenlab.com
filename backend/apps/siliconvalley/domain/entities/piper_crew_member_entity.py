from __future__ import annotations

from dataclasses import dataclass

from siliconvalley.domain.value_objects.piper_role_vo import PiperRole


@dataclass(frozen=True)
class PiperCrewMember:
    """Piper 크루 구성원 — 식별자(id)를 가진 도메인 엔티티."""

    id: int
    name: str
    role: PiperRole
