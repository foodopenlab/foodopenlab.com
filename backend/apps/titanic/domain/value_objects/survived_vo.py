from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class SurvivedType(int, Enum):
    NO = 0
    YES = 1


@dataclass(frozen=True)
class Survived:
    """생존 여부 (survived).

    0 = 사망 (No), 1 = 생존 (Yes)
    """

    value: SurvivedType

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> Survived:
        if raw is None or raw.strip() == "":
            raise ValueError("survived는 필수 값입니다.")
        try:
            return cls(value=SurvivedType(int(raw.strip())))
        except (ValueError, KeyError):
            raise ValueError(f"survived 유효하지 않은 값: '{raw}'") from None

    @classmethod
    def from_optional_raw(cls, raw: Optional[str]) -> Optional[Survived]:
        if raw is None or raw.strip() == "":
            return None
        return cls.from_raw(raw)

    @property
    def is_survived(self) -> bool:
        return self.value == SurvivedType.YES

    def __str__(self) -> str:
        return str(self.value.value)
