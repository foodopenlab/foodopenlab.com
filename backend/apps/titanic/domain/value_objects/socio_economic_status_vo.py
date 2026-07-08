from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.pclass_vo import PClass


@dataclass(frozen=True)
class SocioEconomicStatus:
    """사회·경제적 지위(SES) — survived와 강한 상관을 갖는 임베디드 값 타입.

  Hartley 상관분석 기준:
  - pclass: -0.34
  - cabin:  +0.30
  - fare:   +0.26
    """

    pclass: PClass
    fare: Fare
    cabin: Cabin | None

    @classmethod
    def from_raw(
        cls,
        pclass_raw: Optional[str],
        fare_raw: Optional[str],
        cabin_raw: Optional[str] = None,
    ) -> SocioEconomicStatus:
        return cls(
            pclass=PClass.from_raw(pclass_raw),
            fare=Fare.from_raw(fare_raw),
            cabin=Cabin.from_optional_raw(cabin_raw),
        )

    @property
    def deck(self) -> Optional[str]:
        return self.cabin.deck if self.cabin is not None else None

    @property
    def is_upper_class(self) -> bool:
        return self.pclass.is_first_class
