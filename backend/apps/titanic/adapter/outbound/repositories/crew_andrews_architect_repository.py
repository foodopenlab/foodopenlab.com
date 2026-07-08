from __future__ import annotations

import asyncio
import logging
import os
from typing import Any, cast

from kiwipiepy import Kiwi, Token
from sqlalchemy.ext.asyncio import AsyncSession

from titanic.app.dtos.crew_andrews_architect_dto import AndrewsArchitectQuery, AndrewsArchitectResponse

logger = logging.getLogger(__name__)

INTENT_MAP: dict[str, frozenset[str]] = {
    "FEATURE_IMPORTANCE": frozenset(
        {"중요", "요인", "상관", "변수", "피처", "영향", "feature", "correlation", "ranking"}
    ),
    "DEMOGRAPHIC": frozenset(
        {"남성", "여성", "남자", "여자", "나이", "age", "male", "female"}
    ),
    "SURVIVAL_PREDICT": frozenset(
        {"생존", "예측", "죽", "사망", "survived", "survival", "predict"}
    ),
    "STATISTICS": frozenset(
        {
            "통계", "평균", "비율", "분포", "몇", "count", "stats", "statistics",
            "생존자", "명", "사망자", "생존율",
        }
    ),
    "PASSENGER_SEARCH": frozenset(
        {"승객", "검색", "이름", "찾", "passenger", "search", "who"}
    ),
    "MODEL_TRAIN": frozenset(
        {"학습", "훈련", "모델", "train", "training", "fit"}
    ),
}

_INTENT_PRIORITY: tuple[str, ...] = (
    "FEATURE_IMPORTANCE",
    "DEMOGRAPHIC",
    "STATISTICS",
    "MODEL_TRAIN",
    "PASSENGER_SEARCH",
    "SURVIVAL_PREDICT",
)

_DEFAULT_OLLAMA_MODEL = "anpigon/eeve-korean-10.8b:latest"
_DEFAULT_SYSTEM = (
    "당신은 타이타닉 호 승객 데이터를 돕는 조언자입니다. "
    "짧고 명확한 한국어로 답하세요."
)


class AndrewsArchitectRepository:

    def __init__(self, session: AsyncSession | None = None) -> None:
        self.session = session
        self.kiwi = Kiwi()

    def analyze_intent(self, question: str) -> dict[str, Any]:
        '''Kiwi 형태소 분석으로 질문 의도를 파악하는 레포지토리 구현 메소드'''
        tokens = cast(list[Token], self.kiwi.tokenize(question))
        keywords = [t.form for t in tokens if t.tag.startswith(("NN", "VV", "VA", "XR"))]

        scores: dict[str, int] = {intent: 0 for intent in INTENT_MAP}
        for keyword in keywords:
            for intent, kw_set in INTENT_MAP.items():
                if keyword in kw_set:
                    scores[intent] += 1

        best_score = max(scores.values())
        if best_score <= 0:
            intent = "UNKNOWN"
        else:
            candidates = [name for name, score in scores.items() if score == best_score]
            intent = min(candidates, key=lambda name: _INTENT_PRIORITY.index(name))

        logger.info(
            "[AndrewsArchitectRepository] analyze_intent | question=%r intent=%s scores=%s",
            question, intent, scores,
        )
        return {
            "intent": intent,
            "keywords": keywords,
            "scores": scores,
            "tokens": [(t.form, str(t.tag)) for t in tokens],
        }

    def _respond_sync(self, message: str, context: str | None) -> str:
        import ollama

        model = os.getenv("OLLAMA_MODEL", _DEFAULT_OLLAMA_MODEL)
        cleaned = self.kiwi.space(message)
        system = context or _DEFAULT_SYSTEM
        response = ollama.chat(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": cleaned},
            ],
        )
        content = response.message.content
        if not content or not content.strip():
            return "응답을 생성하지 못했습니다."
        return content.strip()

    async def respond(self, message: str, context: str | None = None) -> str:
        '''Ollama로 자연어 응답 생성 (blocking I/O → thread)'''
        try:
            return await asyncio.to_thread(self._respond_sync, message, context)
        except Exception as exc:
            logger.warning("[AndrewsArchitectRepository] Ollama 실패 | error=%s", exc)
            return (
                "Ollama에 연결할 수 없습니다. "
                "로컬 Ollama 실행 및 OLLAMA_MODEL 설정을 확인해 주세요."
            )

    async def introduce_myself(self, query: AndrewsArchitectQuery) -> AndrewsArchitectResponse:
        '''앤드류 설계자의 자기 소개 레포지토리 구현 메소드'''

        logger.info("[AndrewsArchitectRepository] introduce_myself | request_data=%s", query)

        return AndrewsArchitectResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴",
        )
