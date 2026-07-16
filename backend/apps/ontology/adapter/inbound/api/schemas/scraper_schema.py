from pydantic import BaseModel, Field


class ScrapeRunRequest(BaseModel):
    max_items: int = Field(50, ge=1, le=1000, description="처리할 최대 URL 개수")


class ScrapeRunResponse(BaseModel):
    urls_processed: int
    items_scraped: int
