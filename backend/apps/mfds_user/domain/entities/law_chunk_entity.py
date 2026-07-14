from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LawChunk:
    """법령·고시·판례 등 문서 조문 청크 (pgvector 시맨틱 검색 단위)."""

    id: int
    source_type: str
    law_nm: str
    article_no: str
    article_title: str
    content: str
    enforce_dt: str | None = None
    similarity: float = 0.0
