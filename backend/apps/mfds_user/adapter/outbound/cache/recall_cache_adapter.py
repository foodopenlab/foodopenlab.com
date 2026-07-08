import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional, Any
from zoneinfo import ZoneInfo

from mfds_user.app.ports.output.recall_cache_port import RecallCachePort

logger = logging.getLogger(__name__)
KST = ZoneInfo("Asia/Seoul")

def mfds_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"

class RecallCacheAdapter(RecallCachePort):
    _lock = threading.Lock()
    _cached_items: List[dict] = []
    _cached_is_today: bool = False
    _cached_matched_date: Optional[str] = None
    _last_fetched_at: Optional[datetime] = None
    _last_error: Optional[str] = None

    def __init__(self) -> None:
        self.cache_path = mfds_data_dir() / "recall_cache.json"
        self.catalog_path = mfds_data_dir() / "recall_catalog.json"
        self.sync_state_path = mfds_data_dir() / "food_safety_sync_state.json"
        self._load_cache_file()

    def _normalize_items(self, raw: Any) -> List[dict]:
        if not raw:
            return []
        if not isinstance(raw, list):
            return []
        out: List[dict] = []
        for entry in raw:
            if isinstance(entry, dict) and entry.get("product_name"):
                out.append({k: str(entry.get(k) or "") for k in (
                    "product_name", "reason", "business_name", "registered_at",
                    "recall_grade", "food_type", "serial_no",
                )})
            elif isinstance(entry, list):
                out.extend(self._normalize_items(entry))
        return out

    def _load_cache_file(self) -> None:
        if not self.cache_path.is_file():
            return
        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            RecallCacheAdapter._cached_items = self._normalize_items(data.get("items"))
            RecallCacheAdapter._cached_is_today = bool(data.get("is_today", False))
            RecallCacheAdapter._cached_matched_date = data.get("matched_date")
            raw_at = data.get("fetched_at")
            RecallCacheAdapter._last_fetched_at = datetime.fromisoformat(raw_at).astimezone(KST) if raw_at else None
            RecallCacheAdapter._last_error = data.get("error")
        except Exception as e:
            logger.warning("Recall cache load failed: %s", e)

    def get_latest_recalls_cache(self) -> Tuple[List[dict], Optional[datetime], bool, Optional[str]]:
        with RecallCacheAdapter._lock:
            # reload if empty and file exists
            if not RecallCacheAdapter._cached_items and self.cache_path.is_file():
                self._load_cache_file()
            
            # If there's an error and no items/fetched_at, raise ValueError
            if not RecallCacheAdapter._cached_items and RecallCacheAdapter._last_error and not RecallCacheAdapter._last_fetched_at:
                raise ValueError(RecallCacheAdapter._last_error)

            return (
                list(RecallCacheAdapter._cached_items),
                RecallCacheAdapter._last_fetched_at,
                RecallCacheAdapter._cached_is_today,
                RecallCacheAdapter._cached_matched_date
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

    def list_distinct_food_types_from_disk(self) -> List[str]:
        if not self.catalog_path.is_file():
            return []
        try:
            data = json.loads(self.catalog_path.read_text(encoding="utf-8"))
            items = self._normalize_items(data.get("items"))
            types = set()
            for item in items:
                ft = item.get("food_type", "").strip()
                if ft:
                    types.add(ft)
            return sorted(list(types))
        except Exception as e:
            logger.warning("Recall catalog read failed: %s", e)
            return []
