from pydantic import BaseModel, Field


class ScoutRunRequest(BaseModel):
    mode: str = Field(..., pattern="^(crawler|scraper)$", description="실행 모드")
    url: str = Field(..., min_length=1, description="시드/대상 사이트 URL")
    command: str = Field("", description="자연어 실행 명령")

    model_config = {
        "json_schema_extra": {
            "example": {
                "mode": "crawler",
                "url": "https://example.com",
                "command": "식품 안전 관련 페이지를 깊이 2로 30페이지까지 수집해줘",
            }
        }
    }


class ScoutPlanSchema(BaseModel):
    max_pages: int = Field(..., description="크롤러 방문 최대 페이지 수")
    max_depth: int = Field(..., description="시드로부터 탐색 깊이")
    max_items: int = Field(..., description="스크래퍼 처리 최대 URL 수")
    keywords: list[str] = Field(..., description="해석된 키워드")
    reason: str = Field(..., description="명령 해석 요약(한국어)")


class ScoutRunResponse(BaseModel):
    mode: str = Field(..., description="실행 모드")
    plan: ScoutPlanSchema = Field(..., description="자연어 해석 결과 실행 계획")
    summary: dict = Field(..., description="실행 결과 요약(모드별 키)")


class ScoutResultsResponse(BaseModel):
    kind: str = Field(..., description="결과 종류(crawled|scraped)")
    count: int = Field(..., description="반환된 행 수")
    items: list[dict] = Field(..., description="최신순 결과 행")
