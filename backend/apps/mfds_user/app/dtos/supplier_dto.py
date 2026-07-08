from dataclasses import dataclass, field
from typing import Optional, List, Literal

RiskLevel = Literal["HIGH", "MEDIUM", "LOW", "NONE"]

@dataclass(frozen=True)
class SupplierRiskRecallBriefDTO:
    id: str
    product_name: str
    manufacturer: str = ""
    recall_grade: Optional[int] = None
    registered_at: Optional[str] = None
    recall_reason: Optional[str] = None

@dataclass(frozen=True)
class SupplierRiskEnforcementBriefDTO:
    id: str
    business_name: str = ""
    process_type: Optional[str] = None
    process_date: Optional[str] = None
    violation_content: Optional[str] = None

@dataclass(frozen=True)
class SupplierLicenseBriefDTO:
    found: bool = False
    status: Optional[str] = None
    business_type: Optional[str] = None
    license_number: Optional[str] = None
    demo: bool = False

@dataclass(frozen=True)
class SupplierHaccpCertificationBriefDTO:
    found: bool = False
    certified: bool = False
    certificate_number: Optional[str] = None
    expiry_date: Optional[str] = None
    designated_date: Optional[str] = None
    certified_products: List[str] = field(default_factory=list)
    demo: bool = False

@dataclass(frozen=True)
class SupplierRiskCardDTO:
    business_name: str
    overall_risk: RiskLevel
    summary: str
    recall_count: int = 0
    enforcement_count: int = 0
    recalls: List[SupplierRiskRecallBriefDTO] = field(default_factory=list)
    enforcements: List[SupplierRiskEnforcementBriefDTO] = field(default_factory=list)
    license: Optional[SupplierLicenseBriefDTO] = None
    haccp_certification: Optional[SupplierHaccpCertificationBriefDTO] = None
