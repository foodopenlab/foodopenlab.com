from __future__ import annotations

import re
from typing import Any

import pandas as pd

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse
from titanic.app.ports.input.crew_andrews_architect_use_case import AndrewsArchitectUseCase
from titanic.domain.value_objects.survival_predictors_vo import SurvivalPredictors

_FEATURE_LABELS = {
    "gender": "성별",
    "cabin": "객실(데크)",
    "fare": "요금",
    "pclass": "승객 등급",
}


class AndrewsArchitectInteractor(AndrewsArchitectUseCase):

    def __init__(self, repository) -> None:
        self.repository = repository

    def analyze_intent(self, message: str) -> dict[str, Any]:
        return self.repository.analyze_intent(message)

    async def respond(self, message: str, context: str | None = None) -> str:
        return await self.repository.respond(message, context)

    def _format_train_statistics(self, train_stats: dict[str, Any]) -> str:
        total = train_stats.get("total", 0)
        if not total:
            return "학습 승객 데이터가 없습니다. James 업로드 또는 DB를 확인해 주세요."
        survived = train_stats.get("survived", 0)
        deceased = train_stats.get("deceased", 0)
        rate = train_stats.get("survival_rate", 0.0)
        return (
            f"학습 승객 {total}명 중 생존 {survived}명, 사망 {deceased}명 "
            f"(생존율 {rate}%)."
        )

    def _format_ml_summary(self, trained: dict[str, Any], scores: dict[str, Any]) -> str:
        champion = scores.get("champion") or {}
        name = champion.get("name", "없음")
        accuracy = champion.get("accuracy")
        acc_text = f"{accuracy * 100:.1f}%" if accuracy is not None else "N/A"
        models = ", ".join(trained.get("trained_models", [])) or "없음"
        return (
            f"학습 완료 ({trained.get('train_samples', 0)}명). "
            f"챔피언 모델: {name} (검증 정확도 {acc_text}). "
            f"학습된 모델: {models}."
        )

    def _format_feature_importance(self) -> str:
        ranking = SurvivalPredictors.correlation_ranking()
        lines = [
            f"{index}. {_FEATURE_LABELS.get(name, name)} (상관계수 {coef:+.2f})"
            for index, (name, coef) in enumerate(ranking, start=1)
        ]
        return "생존과 상관이 큰 요인 순서입니다.\n" + "\n".join(lines)

    def _parse_demographic_filters(self, message: str) -> dict[str, int | str | None]:
        age_match = re.search(r"(\d+)\s*살", message)
        age = int(age_match.group(1)) if age_match else None
        gender = None
        if any(token in message for token in ("남성", "남자")):
            gender = "male"
        elif any(token in message for token in ("여성", "여자")):
            gender = "female"
        return {"age": age, "gender": gender}

    def _format_demographic_survival(self, train_set: pd.DataFrame, message: str) -> str | None:
        filters = self._parse_demographic_filters(message)
        if filters["gender"] is None and filters["age"] is None:
            return None

        frame = train_set.copy()
        if filters["gender"] is not None:
            frame = frame[frame["gender"] == filters["gender"]]
        if filters["age"] is not None:
            ages = pd.Series(pd.to_numeric(frame["age"], errors="coerce"))
            age = int(filters["age"])
            frame = frame[ages.between(age - 5, age + 5)]

        if len(frame) == 0:
            return "조건에 맞는 승객 데이터를 찾지 못했습니다."

        labels = pd.Series(pd.to_numeric(frame["survived"], errors="coerce")).fillna(0)
        survived = int(labels.astype(int).sum())
        total = len(frame)
        rate = round(survived / total * 100, 1)

        segment_parts: list[str] = []
        if filters["age"] is not None:
            segment_parts.append(f"{filters['age']}세 전후")
        if filters["gender"] == "male":
            segment_parts.append("남성")
        elif filters["gender"] == "female":
            segment_parts.append("여성")
        segment = " ".join(segment_parts)

        return (
            f"학습 데이터 기준 {segment} 승객 {total}명 중 "
            f"생존 {survived}명 (생존율 {rate}%)."
        )

    def _build_ollama_context(
        self,
        *,
        train_stats: dict[str, Any],
        trained: dict[str, Any],
        scores: dict[str, Any],
    ) -> str:
        return "\n".join([
            self._format_train_statistics(train_stats),
            self._format_ml_summary(trained, scores),
            self._format_feature_importance(),
        ])

    async def compose_chat_reply(
        self,
        message: str,
        *,
        train_set: pd.DataFrame,
        train_stats: dict[str, Any],
        trained: dict[str, Any],
        scores: dict[str, Any],
    ) -> str:
        '''의도 분석 후 통계·ML·Ollama 응답 선택 (Smith는 crew 결과만 넘김)'''
        if not message.strip():
            return "메시지를 입력해 주세요."

        demographic = self._format_demographic_survival(train_set, message)
        if demographic is not None:
            return demographic

        intent = self.analyze_intent(message)["intent"]

        if intent == "FEATURE_IMPORTANCE":
            return self._format_feature_importance()
        if intent == "MODEL_TRAIN":
            return self._format_ml_summary(trained, scores)
        if intent == "STATISTICS":
            return self._format_train_statistics(train_stats)

        context = self._build_ollama_context(
            train_stats=train_stats,
            trained=trained,
            scores=scores,
        )
        return await self.respond(message, context=context)

    async def introduce_myself(self, query: AndrewsArchitectQuery) -> AndrewsArchitectResponse:
        return await self.repository.introduce_myself(query)
