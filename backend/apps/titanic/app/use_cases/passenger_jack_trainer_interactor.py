from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

from sklearn.model_selection import train_test_split

from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.ports.input.passenger_jack_trainer_use_case import JackTrainerUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import SurvivalModelStrategy

logger = logging.getLogger(__name__)


class JackTrainerInteractor(JackTrainerUseCase):

    def __init__(
        self,
        repository: Any,
        build_strategies: Callable[[], dict[str, type[SurvivalModelStrategy]]],
    ):
        self.repository = repository
        self._build_strategies = build_strategies
        self._trained_strategies: dict = {}

    async def train_model(
        self,
        x_train: list[list[float]],
        y_train: list[int],
    ) -> dict[str, Any]:
        '''Lowe (X, y) → holdout split → Rose 전략 fit. Cal 채점용 x_test/y_test 포함 반환'''
        logger.info("[JackTrainerInteractor] 학습 파이프라인 시작 | samples=%s", len(x_train))

        x_fit, x_val, y_fit, y_val = train_test_split(
            x_train, y_train, test_size=0.2, random_state=42, stratify=y_train,
        )

        self._trained_strategies = {}
        trained_names = []
        for key, StrategyClass in self._build_strategies().items():
            strategy = StrategyClass()
            try:
                strategy.fit(x_fit, y_fit)
                self._trained_strategies[key] = strategy
                trained_names.append(strategy.name)
                logger.info("[JackTrainerInteractor] %s 학습 완료", strategy.name)
            except Exception as e:
                logger.warning("[JackTrainerInteractor] %s 학습 실패 | error=%s", key, e)

        return {
            "train_samples": len(x_fit),
            "trained_models": trained_names,
            "trained_strategies": self._trained_strategies,
            "x_test": x_val,
            "y_test": y_val,
        }

    async def introduce_myself(self, query: JackTrainerQuery) -> JackTrainerResponse:
        return await self.repository.introduce_myself(query)
