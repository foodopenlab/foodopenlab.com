from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar, Optional

from titanic.domain.value_objects.gender_vo import Gender
from titanic.domain.value_objects.socio_economic_status_vo import SocioEconomicStatus


@dataclass(frozen=True)
class SurvivalPredictors:
    """survived 예측과 상관이 높은 피처 묶음 (Hartley 히트맵 분석 기준).

    gender는 단독 강한 예측 변수, pclass·fare·cabin은 SES 임베디드 타입으로 묶습니다.
    """

    gender: Gender
    ses: SocioEconomicStatus

    # survived 기준 상관계수 — 양의 상관 큰 순 → 음의 상관 큰 순
    SURVIVED_CORRELATIONS: ClassVar[tuple[tuple[str, float], ...]] = (
        ("gender", 0.54),
        ("cabin", 0.30),
        ("fare", 0.26),
        ("pclass", -0.34),
    )

    @classmethod
    def from_raw(
        cls,
        *,
        gender_raw: Optional[str],
        pclass_raw: Optional[str],
        fare_raw: Optional[str],
        cabin_raw: Optional[str] = None,
    ) -> SurvivalPredictors:
        return cls(
            gender=Gender.from_raw(gender_raw),
            ses=SocioEconomicStatus.from_raw(pclass_raw, fare_raw, cabin_raw),
        )

    @classmethod
    def correlation_ranking(cls) -> list[tuple[str, float]]:
        return sorted(
            cls.SURVIVED_CORRELATIONS,
            key=lambda item: item[1],
            reverse=True,
        )

    def to_feature_vector(self) -> list[float]:
        """상관 분석에 사용된 수치 피처 벡터 [gender, pclass, fare, cabin_deck]."""
        deck_codes = {"A": 1.0, "B": 2.0, "C": 3.0, "D": 4.0, "E": 5.0, "F": 6.0, "G": 7.0}
        deck = self.ses.deck
        cabin_code = deck_codes.get(deck, 0.0) if deck else 0.0
        return [
            float(self.gender.is_female),
            float(self.ses.pclass.value.value),
            self.ses.fare.value,
            cabin_code,
        ]
