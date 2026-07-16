from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.crawler_schema import (
    CrawlRunRequest,
    CrawlRunResponse,
)
from ontology.app.dtos.crawl_dto import CrawlRequest
from ontology.app.ports.input.crawler_use_case import ICrawlerUseCase
from ontology.dependencies.crawler_provider import get_crawler_use_case

router = APIRouter(prefix="/crawler", tags=["crawler"])


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "crawler"}


@router.post("/run", response_model=CrawlRunResponse)
async def run(
    body: CrawlRunRequest,
    use_case: ICrawlerUseCase = Depends(get_crawler_use_case),
) -> CrawlRunResponse:
    report = await use_case.crawl(
        CrawlRequest(max_pages=body.max_pages, max_depth=body.max_depth)
    )
    return CrawlRunResponse(
        seed=report.seed,
        keywords=report.keywords,
        pages_visited=report.pages_visited,
        urls_enqueued=report.urls_enqueued,
    )
