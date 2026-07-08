from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ApiLogItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="로그 UUID")
    api_name: str = Field(..., description="API 이름")
    endpoint: Optional[str] = Field(default=None, description="호출 엔드포인트")
    status_code: Optional[int] = Field(default=None, description="HTTP 상태 코드")
    response_ms: Optional[int] = Field(default=None, description="응답 시간(ms)")
    is_cache_hit: bool = Field(False, description="캐시 히트 여부")
    called_at: datetime = Field(..., description="호출 시각")


class ApiLogListResponse(BaseModel):
    total: int = Field(..., description="전체 건수")
    page: int = Field(..., ge=1, description="현재 페이지")
    items: List[ApiLogItemSchema] = Field(default_factory=list, description="API 로그 목록")

    model_config = {
        "json_schema_extra": {
            "example": {
                "total": 1,
                "page": 1,
                "items": [
                    {
                        "id": "660e8400-e29b-41d4-a716-446655440001",
                        "api_name": "recall_list",
                        "endpoint": "/api/recalls",
                        "status_code": 200,
                        "response_ms": 120,
                        "is_cache_hit": True,
                        "called_at": "2026-06-15T10:00:00",
                    }
                ],
            }
        }
    }


class SearchLogItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="로그 UUID")
    actor_type: str = Field(..., description="행위자 유형")
    actor_id: UUID = Field(..., description="행위자 UUID")
    keyword: str = Field(..., description="검색 키워드")
    query_pattern: str = Field(..., description="질의 패턴")
    searched_at: datetime = Field(..., description="검색 시각")


class SearchLogListResponse(BaseModel):
    total: int = Field(..., description="전체 건수")
    page: int = Field(..., ge=1, description="현재 페이지")
    items: List[SearchLogItemSchema] = Field(default_factory=list, description="검색 로그 목록")


class UsersBlockSchema(BaseModel):
    total: int = Field(..., description="전체 사용자 수")
    active: int = Field(..., description="활성 사용자 수")


class ChatsBlockSchema(BaseModel):
    today_total: int = Field(..., description="오늘 채팅 수")
    analysis_total: int = Field(..., description="분석 채팅 수")
    regulation_total: int = Field(..., description="법령 채팅 수")
    ingredient_total: int = Field(0, description="원재료 채팅 수")


class ApiBlockSchema(BaseModel):
    today_calls: int = Field(..., description="오늘 API 호출 수")
    today_errors: int = Field(..., description="오늘 API 오류 수")
    top_api: str = Field(..., description="최다 호출 API")


class DashboardResponse(BaseModel):
    users: UsersBlockSchema = Field(..., description="사용자 통계")
    chats: ChatsBlockSchema = Field(..., description="채팅 통계")
    api: ApiBlockSchema = Field(..., description="API 통계")

    model_config = {
        "json_schema_extra": {
            "example": {
                "users": {
                    "total": 100,
                    "active": 80,
                },
                "chats": {
                    "today_total": 50,
                    "analysis_total": 20,
                    "regulation_total": 15,
                    "ingredient_total": 5,
                },
                "api": {
                    "today_calls": 1200,
                    "today_errors": 3,
                    "top_api": "recall_list",
                },
            }
        }
    }


class AdminApiStatItemSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    api_name: str = Field(..., description="API 이름")
    total_calls: int = Field(..., description="총 호출 수")
    cache_hits: int = Field(..., description="캐시 히트 수")
    cache_hit_rate: float = Field(..., description="캐시 히트율")
    avg_response_ms: float = Field(..., description="평균 응답 시간(ms)")
    error_count: int = Field(..., description="오류 수")
    error_rate: float = Field(..., description="오류율")


class AdminApiStatsSchema(BaseModel):
    period: str = Field(..., description="집계 기간")
    stats: List[AdminApiStatItemSchema] = Field(default_factory=list, description="API별 통계")

    model_config = {
        "json_schema_extra": {
            "example": {
                "period": "7d",
                "stats": [
                    {
                        "api_name": "recall_list",
                        "total_calls": 500,
                        "cache_hits": 400,
                        "cache_hit_rate": 0.8,
                        "avg_response_ms": 95.5,
                        "error_count": 2,
                        "error_rate": 0.004,
                    }
                ],
            }
        }
    }
