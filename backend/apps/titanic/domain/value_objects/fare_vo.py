from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Fare:
    value: float

    @classmethod
    def from_raw(cls, raw: Optional[str]) -> Fare:
        if raw is None or raw.strip() == "":
            raise ValueError("Fare는 필수 값입니다.")
        try:
            amount = float(raw.strip())
        except ValueError:
            raise ValueError(f"Fare 유효하지 않은 값: '{raw}'") from None
        if amount < 0:
            raise ValueError(f"Fare는 0 이상이어야 합니다: {amount}")
        return cls(value=amount)

    @classmethod
    def from_optional_raw(cls, raw: Optional[str]) -> Optional[Fare]:
        if raw is None or raw.strip() == "":
            return None
        return cls.from_raw(raw)

    def __str__(self) -> str:
        return str(self.value)
