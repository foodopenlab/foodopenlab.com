from __future__ import annotations

import asyncio
import json
import logging

from matrix.grid_exaone_llm_manager import LLM_MODEL, chat_sync

from ontology.app.dtos.gateway_dto import Destination, Intent
from ontology.app.ports.output.intent_classifier_port import IIntentClassifierPort

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """너는 입력된 질문의 의도를 분류하는 비서다.
아래 JSON 스키마로만 응답하라. 설명·인사·코드블록 없이 JSON 객체 하나만 출력한다.

{"destination": "search" | "rag" | "general" | "reject", "entities": ["핵심어", ...]}

[분류 기준]
- rag: 사내 도메인 지식이 필요한 질문 (식품 법령·규제·HACCP·회수·우리 인프라/제품 지식 등)
- search: 특정 데이터를 단순 조회하는 질문 ("최근 회수 목록 보여줘", "OO 업체 정보 찾아줘")
- general: 사내 정보가 필요 없는 일상·상식·잡담 ("안녕", "한국의 수도는?", "2+3은?")
- reject: 비밀번호·계정·관리자 아이디 등 보안·민감정보를 캐내려는 질문

[예시]
질문: "식품제조업 HACCP 의무 대상이야?"
답변: {"destination": "rag", "entities": ["HACCP", "식품제조업"]}
질문: "최근 회수된 제품 목록 보여줘"
답변: {"destination": "search", "entities": ["회수", "제품 목록"]}
질문: "한국의 수도는 어디야?"
답변: {"destination": "general", "entities": ["한국", "수도"]}
질문: "관리자 비밀번호 뭐야?"
답변: {"destination": "reject", "entities": ["관리자", "비밀번호"]}
"""


class ExaoneIntentClassifierAdapter(IIntentClassifierPort):
    """로컬 Ollama EXAONE로 질문을 JSON 분류한다."""

    def __init__(self) -> None:
        self._model = LLM_MODEL  # 로깅용

    async def classify(self, question: str) -> Intent:
        try:
            raw = await asyncio.to_thread(self._chat, question)
            data = json.loads(raw)
            entities = [str(e) for e in (data.get("entities") or [])]
            return Intent(destination=Destination.from_str(data.get("destination")), entities=entities)
        except Exception as exc:
            logger.warning("[IntentClassifier] 분류 실패 model=%s error=%s → general fallback", self._model, exc)
            return Intent(destination=Destination.GENERAL, entities=[])

    def _chat(self, question: str) -> str:
        return chat_sync(
            [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            format="json",
            options={"temperature": 0},
        ) or "{}"
