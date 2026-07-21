from __future__ import annotations

import asyncio
import logging
from typing import Any

from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.ports.input.passenger_cal_tester_use_case import CalTesterUseCase
from titanic.app.ports.input.passenger_rose_model_use_case import SurvivalModelStrategy

logger = logging.getLogger(__name__)


def _score_trained_strategies(test_set: dict[str, Any]) -> dict[str, Any]:
    '''Jack이 학습한 전략들을 (X_test, y_test)로 채점·순위 산정 (CPU-bound)'''
    trained_strategies: dict[str, SurvivalModelStrategy] = test_set["trained_strategies"]
    x_test: list[list[float]] = test_set["x_test"]
    y_test: list[int] = test_set["y_test"]

    results: list[dict[str, Any]] = []
    for key, strategy in trained_strategies.items():
        try:
            predictions = strategy.predict(x_test)
            correct = sum(p == t for p, t in zip(predictions, y_test))
            accuracy = correct / len(y_test)
            results.append({
                "key": key,
                "name": strategy.name,
                "accuracy": round(accuracy, 4),
                "correct": correct,
                "total": len(y_test),
            })
            logger.info("[CalTesterInteractor] %s | accuracy=%.4f", strategy.name, accuracy)
        except Exception as exc:
            results.append({
                "key": key,
                "name": key,
                "accuracy": None,
                "error": str(exc),
            })
            logger.warning("[CalTesterInteractor] %s 채점 실패 | error=%s", key, exc)

    results.sort(key=lambda row: row.get("accuracy") or -1, reverse=True)
    for index, row in enumerate(results):
        row["rank"] = index + 1

    champion = results[0] if results else None
    logger.info("[CalTesterInteractor] 챔피언 결정 | %s", champion)

    return {
        "test_samples": len(x_test),
        "champion": champion,
        "ranking": results,
    }


class CalTesterInteractor(CalTesterUseCase):

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    async def test_model(self, test_set: dict[str, Any]) -> dict[str, Any]:
        '''Jack이 훈련한 로즈 전략들을 채점해 1등을 뽑는 메소드

        Args:
            test_set: {
                "x_test": list[list[float]],  # Lowe.preprocess(test_df) 결과
                "y_test": list[int],
                "trained_strategies": dict[str, SurvivalModelStrategy],
            }
        '''
        logger.info("[CalTesterInteractor] 모델 채점 시작")
        return await asyncio.to_thread(_score_trained_strategies, test_set)

    async def introduce_myself(self, query: CalTesterQuery) -> CalTesterResponse:
        '''칼 테스터의 자기소개 인터렉트'''
        return await self.repository.introduce_myself(query)
