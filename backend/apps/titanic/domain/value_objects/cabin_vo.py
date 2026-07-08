from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Cabin:
    value: str

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> Cabin:
        if raw is None or raw.strip() == "":
            raise ValueError("Cabin은 필수 값입니다.")
        return cls(value=raw.strip())

    @classmethod
    def from_optional_raw(cls, raw: Optional[str]) -> Optional[Cabin]:
        if raw is None or raw.strip() == "":
            return None
        return cls.from_raw(raw)

    @property
    def deck(self) -> Optional[str]:
        """객실 번호 첫 글자 — 선박 구역(Deck A~G)."""
        letter = self.value[0].upper()
        if letter.isalpha():
            return letter
        return None

    def __str__(self) -> str:
        return self.value
