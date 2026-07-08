import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any
from zoneinfo import ZoneInfo

from mfds_user.app.ports.output.enforcement_cache_port import EnforcementCachePort

logger = logging.getLogger(__name__)
KST = ZoneInfo("Asia/Seoul")

def mfds_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"

class EnforcementCacheAdapter(EnforcementCachePort):
    _lock = threading.Lock()
    _cached_items: List[dict] = []
    _cached_is_today: bool = False
    _cached_matched_date: Optional[str] = None
    _last_fetched_at: Optional[datetime] = None
    _last_error: Optional[str] = None

    def __init__(self) -> None:
        self.cache_path = mfds_data_dir() / "sanction_cache.json"
        self.sync_state_path = mfds_data_dir() / "food_safety_sync_state.json"
        self._load_cache_file()

    def _normalize_items(self, raw: Any) -> List[dict]:
        if not raw:
            return []
        if not isinstance(raw, list):
            return []
        out: List[dict] = []
        for entry in raw:
            if isinstance(entry, dict) and entry.get("business_name"):
                out.append({k: str(entry.get(k) or "") for k in (
                    "business_name", "industry", "disposition_date", "disposition_start",
                    "disposition_type", "violation", "address", "representative",
                    "disposition_detail", "agency", "serial_no", "category", "service_id",
                )})
            elif isinstance(entry, list):
                out.extend(self._normalize_items(entry))
        return out

    def _load_cache_file(self) -> None:
        if not self.cache_path.is_file():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            EnforcementCacheAdapter._cached_items = self._normalize_items(data.get("items"))
            EnforcementCacheAdapter._cached_is_today = bool(data.get("is_today", False))
            EnforcementCacheAdapter._cached_matched_date = data.get("matched_date")
            raw_at = data.get("fetched_at")
            EnforcementCacheAdapter._last_fetched_at = datetime.fromisoformat(raw_at).astimezone(KST) if raw_at else None
            EnforcementCacheAdapter._last_error = data.get("error")
        except Exception as e:
            logger.warning("Sanction cache load failed: %s", e)

    def get_latest_sanctions_cache(self) -> Tuple[List[dict], Optional[datetime], bool, Optional[str]]:
        with EnforcementCacheAdapter._lock:
            if not EnforcementCacheAdapter._cached_items and self.cache_path.is_file():
                self._load_cache_file()
            
            if not EnforcementCacheAdapter._cached_items and EnforcementCacheAdapter._last_error and not EnforcementCacheAdapter._last_fetched_at:
                raise ValueError(EnforcementCacheAdapter._last_error)

            return (
                list(EnforcementCacheAdapter._cached_items),
                EnforcementCacheAdapter._last_fetched_at,
                EnforcementCacheAdapter._cached_is_today,
                EnforcementCacheAdapter._cached_matched_date
            )

    def get_public_sync_state(self) -> dict:
        if not self.sync_state_path.is_file():
            return {}
        try:
            data = json.loads(self.sync_state_path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                return {}
            return {
                "last_sync_at": data.get("last_sync_at"),
                "sync_wave": data.get("last_wave"),
                "sync_slot": data.get("last_slot"),
                "morning_sync_at": data.get("morning_sync_at"),
                "afternoon_sync_at": data.get("afternoon_sync_at"),
            }
        except Exception as e:
            logger.warning("Sync state read failed: %s", e)
            return {}
