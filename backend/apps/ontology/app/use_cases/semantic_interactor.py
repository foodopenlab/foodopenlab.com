from __future__ import annotations

import logging
import time

from ontology.app.dtos.semantic_dto import Destination, SemanticQuery, SemanticResult, Intent
from ontology.app.ports.input.semantic_use_case import ISemanticUseCase
from ontology.app.ports.output.audit_log_port import IAuditLogPort
from ontology.app.ports.output.gemini_port import IGeminiPort
from ontology.app.ports.output.intent_classifier_port import IIntentClassifierPort
from ontology.app.ports.output.rag_port import IRagPort
from ontology.app.ports.output.search_port import ISearchPort
from ontology.domain.entities.semantic_audit_log_entity import SemanticAuditLog

logger = logging.getLogger(__name__)

_REJECT_REPLY = "죄송합니다. 보안·민감정보에 대한 요청은 처리할 수 없습니다."
_ANSWER_PREVIEW_LEN = 500


class SemanticInteractor(ISemanticUseCase):
    """
    게이트웨이 두뇌 — 시맨틱 라우팅.

    분류 → 목적지별 위임 → 감사 로그 순으로 처리한다.
    목적지 분기는 조건문이 아니라 핸들러 매핑(dispatch table)으로 처리한다.
    """

    def __init__(
        self,
        classifier: IIntentClassifierPort,
        gemini: IGeminiPort,
        rag: IRagPort,
        search: ISearchPort,
        audit_log: IAuditLogPort,
    ) -> None:
        self._classifier = classifier
        self._gemini = gemini
        self._rag = rag
        self._search = search
        self._audit_log = audit_log
        self._handlers = {
            Destination.GENERAL: self._handle_general,
            Destination.RAG: self._handle_rag,
            Destination.SEARCH: self._handle_search,
            Destination.REJECT: self._handle_reject,
        }

    async def ask(self, query: SemanticQuery) -> SemanticResult:
        started = time.monotonic()
        intent = await self._classifier.classify(query.question)
        answer = await self._handlers[intent.destination](query.question, intent.entities)
        blocked = intent.destination is Destination.REJECT
        latency_ms = int((time.monotonic() - started) * 1000)

        await self._record(query, intent, answer, blocked, latency_ms)
        return SemanticResult(answer=answer, destination=intent.destination.value, blocked=blocked)

    async def _handle_general(self, question: str, entities: list[str]) -> str:
        return await self._gemini.generate(question)

    async def _handle_rag(self, question: str, entities: list[str]) -> str:
        return await self._rag.answer(question, entities)

    async def _handle_search(self, question: str, entities: list[str]) -> str:
        return await self._search.search(question, entities)

    async def _handle_reject(self, question: str, entities: list[str]) -> str:
        return _REJECT_REPLY

    async def _record(
        self, query: SemanticQuery, intent: Intent, answer: str, blocked: bool, latency_ms: int
    ) -> None:
        # 감사 로그 실패가 사용자 응답을 막아서는 안 된다.
        try:
            await self._audit_log.record(
                SemanticAuditLog(
                    question=query.question,
                    destination=intent.destination.value,
                    entities=intent.entities,
                    blocked=blocked,
                    answer_preview=answer[:_ANSWER_PREVIEW_LEN],
                    client_ip=query.client_ip,
                    latency_ms=latency_ms,
                )
            )
        except Exception as exc:
            logger.warning("[SemanticInteractor] 감사 로그 기록 실패: %s", exc)
