from __future__ import annotations

import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_embedding_manager import embed_text
from matrix.grid_exaone_llm_manager import LLM_MODEL, chat_sync
from mfds_user.adapter.outbound.pg.law_chunk_pg_repository import LawChunkPgRepository
from mfds_user.domain.entities.law_chunk_entity import LawChunk

from ontology.app.ports.output.rag_port import IRagPort

logger = logging.getLogger(__name__)

_TOP_K = 6
_LAW_SOURCE_TYPES = ("law", "admrul")  # 법률·시행령·시행규칙 + 고시·행정규칙
_NO_CONTEXT = "관련 법령 조문을 찾지 못했습니다. law.go.kr에서 직접 확인을 권장합니다."


class LawRagAdapter(IRagPort):
    """
    Hub(ontology)가 Spoke(mfds_user)의 법령 RAG 자산을 재사용한다.

    질문 임베딩(bge-m3) → law_chunks pgvector 검색 → EXAONE가 조문을 근거로 답변.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = LawChunkPgRepository(session)
        self._model = LLM_MODEL  # 로깅용

    async def answer(self, question: str, entities: list[str]) -> str:
        embedding = await embed_text(question)
        if embedding is None:
            return _NO_CONTEXT
        hits = await self._repo.search_similar(embedding, top_k=_TOP_K, source_types=_LAW_SOURCE_TYPES)
        if not hits:
            return _NO_CONTEXT
        try:
            return await asyncio.to_thread(self._generate, question, _format_context(hits))
        except Exception as exc:
            logger.warning("[LawRagAdapter] EXAONE 생성 실패 model=%s error=%s", self._model, exc)
            return "일시적으로 답변을 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."

    def _generate(self, question: str, context: str) -> str:
        return chat_sync(
            [
                {"role": "system", "content": _system_prompt(context)},
                {"role": "user", "content": question},
            ],
            options={"temperature": 0.3},
        ) or _NO_CONTEXT


def _format_context(hits: list[LawChunk]) -> str:
    blocks = []
    for h in hits:
        head = f"[{h.law_nm} {h.article_no} {h.article_title}".strip() + "]"
        blocks.append(f"{head}\n{h.content.strip()}")
    return "\n\n".join(blocks)


def _system_prompt(context: str) -> str:
    return f"""너는 한국 식품법규 전문 AI다. 아래 [법령 조문]만 근거로 답하라.
조문에 없는 내용을 지어내지 말고, 법령명과 조문번호를 "출처:"로 밝혀라.
정보가 부족하면 "확인이 필요합니다 — law.go.kr에서 직접 확인을 권장합니다"라고만 답하라.

[법령 조문]
{context}"""
