from __future__ import annotations

from typing import Protocol, Sequence

from mfds_user.domain.entities.law_chunk_entity import LawChunk


class LawChunkRepository(Protocol):
    async def search_similar(
        self,
        embedding: list[float],
        top_k: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[LawChunk]:
        """질문 임베딩과 코사인 유사도가 높은 순으로 청크를 반환한다."""
        ...
