from pydantic import BaseModel, Field


class CrawlRunRequest(BaseModel):
    max_pages: int = Field(20, ge=1, le=500, description="방문할 최대 페이지 수")
    max_depth: int = Field(2, ge=0, le=5, description="시드로부터 탐색할 최대 깊이")


class CrawlRunResponse(BaseModel):
    seed: str | None
    keywords: list[str]
    pages_visited: int
    urls_enqueued: int
