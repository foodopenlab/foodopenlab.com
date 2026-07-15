from __future__ import annotations

import logging

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.adapter.outbound.orm.law_chunk_orm import LawChunkORM

from ontology.app.ports.output.search_port import ISearchPort

logger = logging.getLogger(__name__)

_LIMIT = 10


class LawSearchAdapter(ISearchPort):
    """
    단순 데이터 조회 경로 — law_chunks를 키워드로 매칭해 조문 목록을 반환한다.

    RAG(EXAONE 생성)와 달리 생성 없이 원문 매칭 결과만 목록으로 돌려준다.
    (추후 recalls·suppliers 등 다른 테이블 검색으로 확장 가능)
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def search(self, question: str, entities: list[str]) -> str:
        terms = [t for t in (entities or []) if t.strip()] or [question]
        stmt = (
            select(LawChunkORM.law_nm, LawChunkORM.article_no, LawChunkORM.article_title)
            .where(or_(*[LawChunkORM.content.ilike(f"%{t}%") for t in terms]))
            .limit(_LIMIT)
        )
        rows = (await self._session.execute(stmt)).all()
        if not rows:
            joined = ", ".join(terms)
            return f"'{joined}' 관련 데이터를 찾을 수 없습니다."

        lines = [
            f"- {law_nm} {article_no} {article_title}".rstrip()
            for law_nm, article_no, article_title in rows
        ]
        return "검색 결과:\n" + "\n".join(lines)
