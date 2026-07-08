"""?ㅼ?以??숆린??硫뷀?(留덉?留??깃났 ?쒓컖쨌?ㅼ쟾/?ㅽ썑 援щ텇) ??API ?묐떟쨌UI??"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
KST = ZoneInfo("Asia/Seoul")

def mfds_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"

def _read() -> dict:
    path = mfds_data_dir() / "food_safety_sync_state.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.warning("sync state read failed: %s", e)
        return {}

def _write(data: dict) -> None:
    path = mfds_data_dir() / "food_safety_sync_state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def record_sync_wave_completed(*, wave: str, slot_display: str) -> None:
    now = datetime.now(KST)
    data = _read()
    data["last_wave"] = wave
    data["last_slot"] = slot_display
    data["last_sync_at"] = now.isoformat()
    if wave == "morning":
        data["morning_sync_at"] = now.isoformat()
    elif wave == "afternoon":
        data["afternoon_sync_at"] = now.isoformat()
    _write(data)
    logger.info("food safety sync state saved wave=%s slot=%s", wave, slot_display)

def get_public_sync_state() -> dict:
    data = _read()
    return {
        "last_sync_at": data.get("last_sync_at"),
        "sync_wave": data.get("last_wave"),
        "sync_slot": data.get("last_slot"),
        "morning_sync_at": data.get("morning_sync_at"),
        "afternoon_sync_at": data.get("afternoon_sync_at"),
    }
