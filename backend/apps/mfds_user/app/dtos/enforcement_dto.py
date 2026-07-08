from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class EnforcementDTO:
    id: str
    business_name: str
    business_type: Optional[str] = None
    address: Optional[str] = None
    process_type: Optional[str] = None
    violation_content: Optional[str] = None
    violation_date: Optional[str] = None
    process_date: Optional[str] = None
    district: Optional[str] = None

@dataclass(frozen=True)
class EnforcementListQuery:
    process_type: Optional[str] = None
    business_name: Optional[str] = None
    page: int = 1
    size: int = 20
    user_id: Optional[int] = None
    session_key: Optional[str] = None

@dataclass(frozen=True)
class EnforcementListDTO:
    total: int
    page: int
    items: List[EnforcementDTO]
    empty_label: Optional[str] = None
    last_sync_at: Optional[str] = None
    sync_wave: Optional[str] = None
    sync_slot: Optional[str] = None


@dataclass(frozen=True)
class LatestSanctionItemDTO:
    business_name: str = ""
    industry: str = ""
    disposition_date: str = ""
    disposition_start: str = ""
    disposition_type: str = ""
    violation: str = ""
    address: str = ""
    representative: str = ""
    disposition_detail: str = ""
    agency: str = ""
    serial_no: str = ""
    category: str = ""
    service_id: str = ""


@dataclass(frozen=True)
class LatestSanctionsDTO:
    items: List[LatestSanctionItemDTO]
    fetched_at: Optional[str] = None
    query_date: Optional[str] = None
    is_today: bool = False
    matched_date: Optional[str] = None
    last_sync_at: Optional[str] = None
    sync_wave: Optional[str] = None
    sync_slot: Optional[str] = None
