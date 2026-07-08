from typing import List, Optional

from pydantic import BaseModel, Field


class EnforcementSchema(BaseModel):
    id: str = Field(..., description="행정처분 ID")
    business_name: str = Field(..., description="업소명")
    business_type: Optional[str] = Field(default=None, description="업종")
    address: Optional[str] = Field(default=None, description="주소")
    process_type: Optional[str] = Field(default=None, description="처분 유형")
    violation_content: Optional[str] = Field(default=None, description="위반 내용")
    violation_date: Optional[str] = Field(default=None, description="위반 일자")
    process_date: Optional[str] = Field(default=None, description="처분 일자")
    district: Optional[str] = Field(default=None, description="관할 지역")


class SanctionItemResponse(BaseModel):
    business_name: str = Field("", description="업소명")
    industry: str = Field("", description="업종")
    disposition_date: str = Field("", description="처분일")
    disposition_start: str = Field("", description="처분 시작일")
    disposition_type: str = Field("", description="처분 유형")
    violation: str = Field("", description="위반 내용")
    address: str = Field("", description="주소")
    representative: str = Field("", description="대표자")
    disposition_detail: str = Field("", description="처분 상세")
    agency: str = Field("", description="관할 기관")
    serial_no: str = Field("", description="일련번호")
    category: str = Field("", description="분류")
    service_id: str = Field("", description="공공데이터 서비스 ID")


class LatestSanctionsResponse(BaseModel):
    items: List[SanctionItemResponse] = Field(default_factory=list, description="최신 행정처분 목록")
    fetched_at: Optional[str] = Field(default=None, description="조회 시각")
    query_date: Optional[str] = Field(default=None, description="조회 기준일")
    is_today: bool = Field(False, description="당일 데이터 여부")
    matched_date: Optional[str] = Field(default=None, description="매칭된 데이터 일자")
    last_sync_at: Optional[str] = Field(default=None, description="마지막 스케줄 동기화 시각(KST ISO)")
    sync_wave: Optional[str] = Field(default=None, description="morning | afternoon")
    sync_slot: Optional[str] = Field(default=None, description="09:40 | 17:40")


class EnforcementListResponse(BaseModel):
    total: int = Field(..., description="전체 건수")
    page: int = Field(..., description="현재 페이지")
    items: List[EnforcementSchema] = Field(default_factory=list, description="행정처분 목록")
    list_max: int = Field(20, description="페이지당 최대 건수")
    empty_label: Optional[str] = Field(default=None, description="빈 목록 안내 문구")
    last_sync_at: Optional[str] = Field(default=None, description="마지막 동기화 시각")
    sync_wave: Optional[str] = Field(default=None, description="동기화 wave")
    sync_slot: Optional[str] = Field(default=None, description="동기화 slot")
