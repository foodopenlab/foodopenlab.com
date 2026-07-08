from datetime import date, datetime
from typing import List

from pydantic import BaseModel, Field


class ReportItemSchema(BaseModel):
    title: str = Field(..., description="기사·항목 제목")
    url: str = Field(..., description="원문 URL")
    source: str = Field(..., description="출처")
    published_at: date = Field(..., description="게시일")


class ReportSectionSchema(BaseModel):
    type: str = Field(..., description="섹션 유형")
    items: List[ReportItemSchema] = Field(default_factory=list, description="섹션 항목 목록")
    is_empty: bool = Field(..., description="항목 없음 여부")


class DailyReportSchema(BaseModel):
    id: str = Field(..., description="리포트 UUID")
    expert_user_id: str = Field(..., description="전문가 사용자 UUID")
    report_date: date = Field(..., description="리포트 기준일")
    generated_at: datetime = Field(..., description="생성 시각")
    expires_at: datetime = Field(..., description="만료 시각")
    is_saved: bool = Field(..., description="저장 여부")
    summary: str = Field(..., description="전체 요약")
    summary_preview: str = Field(..., description="요약 미리보기")
    sections: List[ReportSectionSchema] = Field(default_factory=list, description="섹션 목록")

    model_config = {
        "json_schema_extra": {
            "example": {
                "id": "770e8400-e29b-41d4-a716-446655440000",
                "expert_user_id": "550e8400-e29b-41d4-a716-446655440000",
                "report_date": "2026-06-15",
                "generated_at": "2026-06-15T10:30:00",
                "expires_at": "2026-06-16T10:30:00",
                "is_saved": False,
                "summary": "오늘의 식품 안전 브리핑 ...",
                "summary_preview": "오늘의 식품 안전 브리핑 ...",
                "sections": [],
            }
        }
    }


class SchedulerResultSchema(BaseModel):
    success: int = Field(..., description="성공 건수")
    fail: int = Field(..., description="실패 건수")
    skipped: int = Field(..., description="건너뜀 건수")
    total: int = Field(..., description="전체 대상 건수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "success": 16,
                "fail": 0,
                "skipped": 2,
                "total": 18,
            }
        }
    }
