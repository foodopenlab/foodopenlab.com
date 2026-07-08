from typing import List, Optional

from pydantic import BaseModel, Field


class RecallSchema(BaseModel):
    id: str = Field(..., description="회수·판매중지 ID")
    product_name: str = Field(..., description="제품명")
    manufacturer: str = Field(..., description="제조사")
    food_type: Optional[str] = Field(default=None, description="식품 유형")
    food_category: Optional[str] = Field(default=None, description="식품 분류")
    recall_reason: Optional[str] = Field(default=None, description="회수 사유")
    recall_grade: Optional[int] = Field(default=None, description="회수 등급")
    recall_method: Optional[str] = Field(default=None, description="회수 방법")
    registered_at: Optional[str] = Field(default=None, description="등록일")
    image_url: Optional[str] = Field(default=None, description="이미지 URL")
    prdlst_report_no: Optional[str] = Field(default=None, description="품목보고번호")


class RecallFoodTypesResponse(BaseModel):
    items: List[str] = Field(default_factory=list, description="식품 유형 목록")


class RecallListResponse(BaseModel):
    total: int = Field(..., description="전체 건수")
    page: int = Field(..., description="현재 페이지")
    items: List[RecallSchema] = Field(default_factory=list, description="회수 목록")
    display_note: Optional[str] = Field(default=None, description="표시 안내 문구")


class RecallItemResponse(BaseModel):
    product_name: str = Field("", description="제품명")
    reason: str = Field("", description="회수 사유")
    business_name: str = Field("", description="업소명")
    registered_at: str = Field("", description="등록일")
    recall_grade: str = Field("", description="회수 등급")
    food_type: str = Field("", description="식품 유형")
    serial_no: str = Field("", description="일련번호")


class LatestRecallsResponse(BaseModel):
    items: List[RecallItemResponse] = Field(default_factory=list, description="최신 회수 목록")
    fetched_at: Optional[str] = Field(default=None, description="조회 시각")
    query_date: Optional[str] = Field(default=None, description="조회 기준일")
    is_today: bool = Field(False, description="당일 데이터 여부")
    matched_date: Optional[str] = Field(default=None, description="매칭된 데이터 일자")
    last_sync_at: Optional[str] = Field(default=None, description="마지막 스케줄 동기화 시각(KST ISO)")
    sync_wave: Optional[str] = Field(default=None, description="morning | afternoon")
    sync_slot: Optional[str] = Field(default=None, description="09:40 | 17:40")
