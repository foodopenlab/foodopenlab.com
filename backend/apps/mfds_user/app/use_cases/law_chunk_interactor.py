from __future__ import annotations

from typing import Sequence

from matrix.grid_embedding_manager import embed_text

from mfds_user.app.dtos.law_chunk_dto import LawChunkHit
from mfds_user.app.ports.output.law_chunk_repository import LawChunkRepository


class LawChunkInteractor:
    def __init__(self, repo: LawChunkRepository) -> None:
        self._repo = repo

    async def search(
        self,
        query: str,
        top_k: int = 5,
        source_types: Sequence[str] | None = None,
    ) -> list[LawChunkHit]:
        embedding = await embed_text(query)
        if embedding is None:
            return []
        chunks = await self._repo.search_similar(embedding, top_k, source_types)
        return [
            LawChunkHit(
                law_nm=c.law_nm,
                article_no=c.article_no,
                article_title=c.article_title,
                content=c.content,
                source_type=c.source_type,
                similarity=c.similarity,
            )
            for c in chunks
        ]
