from __future__ import annotations

from collections.abc import Callable
from typing import Any

from titanic.app.dtos.passenger_rose_model_dto import RoseModelQuery, RoseModelResponse
from titanic.app.ports.input.passenger_rose_model_use_case import RoseModelUseCase, SurvivalModelStrategy


class RoseModelInteractor(RoseModelUseCase):

    def __init__(
        self,
        repository: Any,
        build_strategies: Callable[[], dict[str, type[SurvivalModelStrategy]]],
        strategy: SurvivalModelStrategy,
    ) -> None:
        self.repository = repository
        self._build_strategies = build_strategies
        self._strategy: SurvivalModelStrategy = strategy

    # ── Strategy Pattern ────────────────────────────────────────────────────────

    def set_strategy(self, strategy: SurvivalModelStrategy) -> None:
        self._strategy = strategy

    async def analyze_rose_survival(self) -> dict[str, Any]:
        return {
            "current_strategy": self._strategy.name,
            "current_description": self._strategy.description,
            "available_strategies": [
                {"rank": i + 1, "key": key, "name": cls().name, "description": cls().description}
                for i, (key, cls) in enumerate(self._build_strategies().items())
            ],
        }

    async def predict_survival(self, passenger_data: dict[str, Any]) -> dict[str, Any]:
        features = _extract_features(passenger_data)
        try:
            prediction = self._strategy.predict([features])[0]
            proba = self._strategy.predict_proba([features])[0]
        except Exception:
            raise RuntimeError(
                f"'{self._strategy.name}' 모델이 학습되지 않았습니다. "
                "predict_survival() 호출 전에 strategy.fit(X, y)를 먼저 실행하세요."
            )
        return {
            "strategy": self._strategy.name,
            "survived": bool(prediction),
            "survival_probability": round(proba, 4),
            "passenger": passenger_data,
        }

    # ── Other Use Cases ─────────────────────────────────────────────────────────

    async def introduce_myself(self, query: RoseModelQuery) -> RoseModelResponse:
        return await self.repository.introduce_myself(query)


def _extract_features(data: dict[str, Any]) -> list[float]:
    """승객 데이터 dict → 수치 피처 [pclass, gender, age, sib_sp, parch, fare]

    피처 순서: titanic-algorithm.md 기준 핵심 6개 변수
    - gender: female=1, male=0 (nominal → binary 인코딩)
    - pclass, age, sib_sp, parch, fare: ratio 척도 수치형
    """
    gender = 1.0 if str(data.get("gender", "male")).lower() == "female" else 0.0
    return [
        float(data.get("pclass", 3)),
        gender,
        float(data.get("age", 30)),
        float(data.get("sib_sp", 0)),
        float(data.get("parch", 0)),
        float(data.get("fare", 32.0)),
    ]
