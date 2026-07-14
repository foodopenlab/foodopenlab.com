from __future__ import annotations

from typing import Protocol, Sequence

from mfds_user.app.dtos.law_chunk_dto import LawChunkHit


class LawChunkSearchUseCase(Protocol):
    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[LawChunkHit]:
        """질문 텍스트를 임베딩해 유사 청크를 검색한다."""
        ...
