"""식품안전나라 OpenAPI 동기화 시각(KST) — 하루 2회, 서비스 간격 호출."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

KST = ZoneInfo("Asia/Seoul")

# (시, 분, wave 라벨) — 매일 09:40 · 17:40 KST 자동 수집
SYNC_SLOT_SPECS = (
    (9, 40, "morning"),
    (17, 40, "afternoon"),
)

DEFAULT_STAGGER_SECONDS = 600

def stagger_seconds(*, manual: bool = False) -> int:
    import os

    if manual:
        raw = (os.getenv("FOOD_SAFETY_MANUAL_STAGGER_SEC") or "60").strip()
    else:
        raw = (os.getenv("FOOD_SAFETY_SYNC_STAGGER_SEC") or "").strip()
    if not raw:
        return 60 if manual else DEFAULT_STAGGER_SECONDS
    try:
        return max(10, int(raw))
    except ValueError:
        return 60 if manual else DEFAULT_STAGGER_SECONDS

def next_sync_slot_kst() -> tuple[datetime, str, str]:
    """?ㅼ쓬 ?숆린???쒓컖, ?쇰꺼(morning/afternoon), ?쒖떆??HH:MM."""
    now = datetime.now(KST)
    best = None
    for hour, minute, label in SYNC_SLOT_SPECS:
        candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if candidate <= now:
            candidate += timedelta(days=1)
        display = f"{hour:02d}:{minute:02d}"
        if best is None or candidate < best[0]:
            best = (candidate, label, display)
    assert best is not None
    return best

def seconds_until_next_sync_slot() -> float:
    target, _, _ = next_sync_slot_kst()
    return max(1.0, (target - datetime.now(KST)).total_seconds())
