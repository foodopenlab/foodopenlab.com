from __future__ import annotations

from pydantic import BaseModel, Field


class LawChunkSearchRequestSchema(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1, le=20)
    source_types: list[str] | None = None


class LawChunkHitSchema(BaseModel):
    law_nm: str
    article_no: str
    article_title: str
    content: str
    source_type: str
    similarity: float


class LawChunkSearchResponseSchema(BaseModel):
    hits: list[LawChunkHitSchema]
