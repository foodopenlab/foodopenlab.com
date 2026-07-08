"""?�품?�전?�라 OpenAPI RESULT.CODE ?�석 (INFO-300 ??."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

_quota_blocked_until: datetime | None = None
_OK_CODES = frozenset({"", "INFO-000", "INFO-200"})
_BLOCK_CODES = frozenset({"INFO-100", "INFO-300", "INFO-400"})

def is_api_quota_blocked() -> bool:
    if _quota_blocked_until is None:
        return False
    return datetime.now(KST) < _quota_blocked_until

def mark_api_quota_blocked() -> None:
    global _quota_blocked_until
    now = datetime.now(KST)
    end = now.replace(hour=23, minute=59, second=59, microsecond=0)
    if now >= end:
        end += timedelta(days=1)
    _quota_blocked_until = end

def clear_api_quota_block_for_new_day() -> None:
    global _quota_blocked_until
    if _quota_blocked_until is None:
        return
    now = datetime.now(KST)
    if now.date() > _quota_blocked_until.astimezone(KST).date():
        _quota_blocked_until = None

def clear_api_quota_block() -> None:
    global _quota_blocked_until
    _quota_blocked_until = None

def check_food_safety_api_result(code: str, msg: str = "") -> None:
    c = (code or "").strip()
    if c in _OK_CODES:
        return
    if c in _BLOCK_CODES:
        if c == "INFO-300":
            mark_api_quota_blocked()
        raise RuntimeError((msg or "").strip() or c)
    if c.startswith("ERROR-"):
        raise RuntimeError((msg or "").strip() or c)
