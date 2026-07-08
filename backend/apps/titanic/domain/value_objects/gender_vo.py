from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class GenderType(str, Enum):
    MALE = "male"
    FEMALE = "female"


@dataclass(frozen=True)
class Gender:
    value: GenderType

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> Gender:
        if raw is None or raw.strip() == "":
            raise ValueError("Gender는 필수 값입니다.")
        normalized = raw.strip().lower()
        try:
            return cls(value=GenderType(normalized))
        except ValueError:
            raise ValueError(f"Gender 유효하지 않은 값: '{raw}'") from None

    @property
    def is_female(self) -> bool:
        return self.value == GenderType.FEMALE

    @property
    def is_male(self) -> bool:
        return self.value == GenderType.MALE

    def __str__(self) -> str:
        return self.value.value
