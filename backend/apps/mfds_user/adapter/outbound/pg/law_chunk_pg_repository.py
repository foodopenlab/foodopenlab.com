from __future__ import annotations

from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.adapter.outbound.orm.law_chunk_orm import LawChunkORM
from mfds_user.app.ports.output.law_chunk_repository import LawChunkRepository
from mfds_user.domain.entities.law_chunk_entity import LawChunk


class LawChunkPgRepository(LawChunkRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def search_similar(
        self,
        embedding: list[float],
        top_k: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[LawChunk]:
        distance = LawChunkORM.embedding.cosine_distance(embedding)
        stmt = select(LawChunkORM, distance.label("distance")).where(
            LawChunkORM.embedding.isnot(None)
        )
        if source_types:
            # 근사(HNSW) 인덱스 + 선택적 필터 조합 시, 전역 최근접 후보가 필터로
            # 모두 걸러져 결과가 비는 문제를 pgvector 0.8 iterative scan으로 해소.
            # SET LOCAL: 현재 트랜잭션에만 적용 → 커넥션 풀 재사용 시 누수 없음.
            await self.session.execute(text("SET LOCAL hnsw.iterative_scan = strict_order"))
            stmt = stmt.where(LawChunkORM.source_type.in_(list(source_types)))
        stmt = stmt.order_by(distance).limit(top_k)

        res = await self.session.execute(stmt)
        return [self._to_entity(orm, dist) for orm, dist in res.all()]

    def _to_entity(self, orm: LawChunkORM, distance: float) -> LawChunk:
        return LawChunk(
            id=orm.id,
            source_type=orm.source_type or "",
            law_nm=orm.law_nm or "",
            article_no=orm.article_no or "",
            article_title=orm.article_title or "",
            content=orm.content or "",
            enforce_dt=orm.enforce_dt,
            similarity=round(1.0 - float(distance), 4),
        )
