from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class RegulationItemSchema(BaseModel):
    law_id: str = Field(..., description="법령 ID")
    title: str = Field(..., description="법령 제목")
    law_type: str = Field(..., description="법령 유형")
    change_type: Optional[str] = Field(default=None, description="개정 유형")
    promulgation_date: Optional[date] = Field(default=None, description="공포일")
    promulgation_no: Optional[str] = Field(default=None, description="공포번호")
    enforcement_date: Optional[date] = Field(default=None, description="시행일")
    source: Optional[str] = Field(default=None, description="출처")
    url: str = Field(..., description="원문 URL")


class RegulationListResponseSchema(BaseModel):
    items: List[RegulationItemSchema] = Field(default_factory=list, description="법령 목록")
    total: int = Field(..., description="전체 건수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": [
                    {
                        "law_id": "001234",
                        "title": "식품위생법",
                        "law_type": "법률",
                        "change_type": "일부개정",
                        "promulgation_date": "2026-01-01",
                        "promulgation_no": "제12345호",
                        "enforcement_date": "2026-07-01",
                        "source": "국가법령정보센터",
                        "url": "https://example.com/law/001234",
                    }
                ],
                "total": 1,
            }
        }
    }
