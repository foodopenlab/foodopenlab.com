from typing import List, Literal, Optional

from pydantic import BaseModel, Field

RiskLevel = Literal["HIGH", "MEDIUM", "LOW", "NONE"]


class SupplierRiskRecallBrief(BaseModel):
    id: str = Field(..., description="회수 ID")
    product_name: str = Field(..., description="제품명")
    manufacturer: str = Field("", description="제조사")
    recall_grade: Optional[int] = Field(default=None, description="회수 등급")
    registered_at: Optional[str] = Field(default=None, description="등록일")
    recall_reason: Optional[str] = Field(default=None, description="회수 사유")


class SupplierRiskEnforcementBrief(BaseModel):
    id: str = Field(..., description="행정처분 ID")
    business_name: str = Field("", description="업소명")
    process_type: Optional[str] = Field(default=None, description="처분 유형")
    process_date: Optional[str] = Field(default=None, description="처분 일자")
    violation_content: Optional[str] = Field(default=None, description="위반 내용")


class SupplierLicenseBrief(BaseModel):
    found: bool = Field(False, description="인허가 조회 성공 여부")
    status: Optional[str] = Field(default=None, description="영업 상태")
    business_type: Optional[str] = Field(default=None, description="업종")
    license_number: Optional[str] = Field(default=None, description="인허가 번호")
    demo: bool = Field(False, description="데모 데이터 여부")


class SupplierHaccpCertificationBrief(BaseModel):
    found: bool = Field(False, description="HACCP 조회 성공 여부")
    certified: bool = Field(False, description="인증 여부")
    certificate_number: Optional[str] = Field(default=None, description="인증서 번호")
    expiry_date: Optional[str] = Field(default=None, description="만료일")
    designated_date: Optional[str] = Field(default=None, description="지정일")
    certified_products: List[str] = Field(default_factory=list, description="인증 품목")
    demo: bool = Field(False, description="데모 데이터 여부")


class SupplierRiskCardResponse(BaseModel):
    business_name: str = Field(..., description="업소명")
    overall_risk: RiskLevel = Field(..., description="종합 위험도")
    summary: str = Field(..., description="위험 요약")
    recall_count: int = Field(0, description="회수 건수")
    enforcement_count: int = Field(0, description="행정처분 건수")
    recalls: List[SupplierRiskRecallBrief] = Field(default_factory=list, description="회수 요약")
    enforcements: List[SupplierRiskEnforcementBrief] = Field(
        default_factory=list,
        description="행정처분 요약",
    )
    license: Optional[SupplierLicenseBrief] = Field(default=None, description="인허가 정보")
    haccp_certification: Optional[SupplierHaccpCertificationBrief] = Field(
        default=None,
        description="HACCP 인증 정보",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "business_name": "예시식품",
                "overall_risk": "LOW",
                "summary": "최근 중대 위반 이력 없음",
                "recall_count": 0,
                "enforcement_count": 0,
                "recalls": [],
                "enforcements": [],
                "license": None,
                "haccp_certification": None,
            }
        }
    }
