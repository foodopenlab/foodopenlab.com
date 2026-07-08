from dataclasses import dataclass
from typing import Optional, List

@dataclass(frozen=True)
class RecallDTO:
    id: str
    product_name: str
    manufacturer: str
    food_type: Optional[str] = None
    food_category: Optional[str] = None
    recall_reason: Optional[str] = None
    recall_grade: Optional[int] = None
    recall_method: Optional[str] = None
    registered_at: Optional[str] = None
    image_url: Optional[str] = None
    prdlst_report_no: Optional[str] = None

@dataclass(frozen=True)
class RecallListQuery:
    food_category: Optional[str] = None
    food_type: Optional[str] = None
    grade: Optional[int] = None
    page: int = 1
    size: int = 20
    user_id: Optional[int] = None
    session_key: Optional[str] = None

@dataclass(frozen=True)
class RecallListDTO:
    total: int
    page: int
    items: List[RecallDTO]
    display_note: Optional[str] = None

@dataclass(frozen=True)
class LatestRecallItemDTO:
    product_name: str = ""
    reason: str = ""
    business_name: str = ""
    registered_at: str = ""
    recall_grade: str = ""
    food_type: str = ""
    serial_no: str = ""

@dataclass(frozen=True)
class LatestRecallsDTO:
    items: List[LatestRecallItemDTO]
    fetched_at: Optional[str] = None
    query_date: Optional[str] = None
    is_today: bool = False
    matched_date: Optional[str] = None
    last_sync_at: Optional[str] = None
    sync_wave: Optional[str] = None
    sync_slot: Optional[str] = None

