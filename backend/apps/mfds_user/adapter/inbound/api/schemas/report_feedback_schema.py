from datetime import date, datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class FeedbackSubmitRequestSchema(BaseModel):
    useful_sections: List[str] = Field(default_factory=list, description="유용했던 섹션")
    content_feedback: Optional[str] = Field(default=None, description="내용 피드백")
    missing_feedback: Optional[str] = Field(default=None, description="누락 피드백")
    improvement_feedback: Optional[str] = Field(default=None, description="개선 피드백")
    usefulness_score: int = Field(..., description="유용성 점수")

    model_config = {
        "json_schema_extra": {
            "example": {
                "useful_sections": ["recall", "regulation"],
                "content_feedback": "회수 정보가 도움이 됐습니다",
                "missing_feedback": None,
                "improvement_feedback": None,
                "usefulness_score": 4,
            }
        }
    }


class FeedbackResponseSchema(BaseModel):
    id: str = Field(..., description="피드백 UUID")
    report_id: str = Field(..., description="리포트 UUID")
    expert_user_id: str = Field(..., description="전문가 UUID")
    created_at: datetime = Field(..., description="제출 시각")
    useful_sections: List[str] = Field(default_factory=list, description="유용했던 섹션")
    content_feedback: Optional[str] = Field(default=None, description="내용 피드백")
    missing_feedback: Optional[str] = Field(default=None, description="누락 피드백")
    improvement_feedback: Optional[str] = Field(default=None, description="개선 피드백")
    usefulness_score: int = Field(..., description="유용성 점수")


class FeedbackAnalysisTriggerRequestSchema(BaseModel):
    industry_code: str = Field(..., description="업종 코드")
    period_start: date = Field(..., description="분석 시작일")
    period_end: date = Field(..., description="분석 종료일")

    model_config = {
        "json_schema_extra": {
            "example": {
                "industry_code": "FT01",
                "period_start": "2026-06-01",
                "period_end": "2026-06-15",
            }
        }
    }


class FeedbackAnalysisResponseSchema(BaseModel):
    id: str = Field(..., description="분석 결과 UUID")
    industry_code: str = Field(..., description="업종 코드")
    analyzed_at: datetime = Field(..., description="분석 시각")
    feedback_count: int = Field(..., description="피드백 건수")
    period_start: date = Field(..., description="분석 시작일")
    period_end: date = Field(..., description="분석 종료일")
    missing_topics: List[str] = Field(default_factory=list, description="누락 주제")
    improvement_keys: List[str] = Field(default_factory=list, description="개선 키워드")
    useful_sections: Dict[str, float] = Field(default_factory=dict, description="섹션별 유용도")
    summary: str = Field(..., description="요약")
    action_items: List[str] = Field(default_factory=list, description="액션 아이템")
