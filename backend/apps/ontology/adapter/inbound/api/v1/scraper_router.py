from fastapi import APIRouter, Depends

from ontology.adapter.inbound.api.schemas.scraper_schema import (
    ScrapeRunRequest,
    ScrapeRunResponse,
)
from ontology.app.dtos.scrape_dto import ScrapeRequest
from ontology.app.ports.input.scraper_use_case import IScraperUseCase
from ontology.dependencies.scraper_provider import get_scraper_use_case

router = APIRouter(prefix="/scraper", tags=["scraper"])


@router.get("/myself")
async def introduce_myself() -> dict:
    return {"id": 0, "name": "scraper"}


@router.post("/run", response_model=ScrapeRunResponse)
async def run(
    body: ScrapeRunRequest,
    use_case: IScraperUseCase = Depends(get_scraper_use_case),
) -> ScrapeRunResponse:
    report = await use_case.scrape(ScrapeRequest(max_items=body.max_items))
    return ScrapeRunResponse(
        urls_processed=report.urls_processed,
        items_scraped=report.items_scraped,
    )
