from fastapi import APIRouter, Depends, HTTPException, status

from mfds_user.adapter.inbound.api.schemas.law_chunk_schema import (
    LawChunkHitSchema,
    LawChunkSearchRequestSchema,
    LawChunkSearchResponseSchema,
)
from mfds_user.app.ports.input.law_chunk_use_case import LawChunkSearchUseCase
from mfds_user.dependencies.law_chunk import get_law_chunk_search_use_case

router = APIRouter(prefix="/law-chunk", tags=["law-chunk"])


@router.get("/myself")
async def myself() -> dict:
    """배선 검증용 — router→use_case→port→repository 없이 최소 왕복."""
    return {"id": 0, "name": "law_chunk"}


@router.post("/search", response_model=LawChunkSearchResponseSchema)
async def search(
    body: LawChunkSearchRequestSchema,
    use_case: LawChunkSearchUseCase = Depends(get_law_chunk_search_use_case),
) -> LawChunkSearchResponseSchema:
    if not body.query.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="query가 필요합니다.")

    hits = await use_case.search(body.query.strip(), body.top_k, body.source_types)
    return LawChunkSearchResponseSchema(
        hits=[
            LawChunkHitSchema(
                law_nm=h.law_nm,
                article_no=h.article_no,
                article_title=h.article_title,
                content=h.content,
                source_type=h.source_type,
                similarity=h.similarity,
            )
            for h in hits
        ]
    )
