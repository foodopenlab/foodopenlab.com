"""외부 API 일일 소프트 한도 (무료 할당의 N% 도달 시 신규 호출 중단).

- Google Gemini, data.go.kr, 법제처, OpenWeather 등 **프로세스 단위** in-memory 카운터.
- 서버 다중 워커·재시작 시 카운트는 리셋됩니다. 엄밀한 전역 쿼터는 Redis 등 별도 저장소가 필요합니다.
- ``EXTERNAL_API_DAILY_UNIT_LIMIT=0`` (기본) → 비활성화.
"""

from __future__ import annotations

import logging
import os
import threading
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_day_utc: str | None = None
_used_units: int = 0


class ExternalApiBudgetExceeded(Exception):
    """일일 소프트 한도에 도달해 외부 호출을 하지 않습니다."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


def _utc_date_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def _read_limit() -> int:
    raw = (os.getenv("EXTERNAL_API_DAILY_UNIT_LIMIT") or "").strip()
    if not raw:
        return 0
    try:
        return max(0, int(raw))
    except ValueError:
        return 0


def _read_soft_percent() -> int:
    raw = (os.getenv("EXTERNAL_API_SOFT_STOP_PERCENT") or "80").strip()
    try:
        return max(1, min(100, int(raw)))
    except ValueError:
        return 80


def _soft_threshold(limit: int, percent: int) -> int:
    """limit의 percent% 미만일 때만 호출 허용 → 누적 used가 threshold 이상이면 차단."""
    if limit <= 0:
        return 0
    return max(1, (limit * percent) // 100)


def get_external_api_usage_state() -> dict[str, int | str]:
    """관측용(로그·헬스). 민감 정보 없음."""
    with _lock:
        return {
            "utc_day": _day_utc or "",
            "used_units": _used_units,
            "daily_limit": _read_limit(),
            "soft_stop_percent": _read_soft_percent(),
            "soft_threshold": _soft_threshold(_read_limit(), _read_soft_percent()),
        }


def consume_external_api_unit_or_raise(*, units: int = 1, label: str = "") -> None:
    """외부 HTTP/Gemini 1회 호출 직전에 호출. 한도 초과 시 ``ExternalApiBudgetExceeded``."""
    limit = _read_limit()
    if limit <= 0:
        return

    pct = _read_soft_percent()
    threshold = _soft_threshold(limit, pct)

    global _day_utc, _used_units
    with _lock:
        today = _utc_date_iso()
        if _day_utc != today:
            _day_utc = today
            _used_units = 0

        if _used_units >= threshold:
            msg = (
                f"외부 API 일일 소프트 한도에 도달했습니다 (사용 {_used_units}/{limit} 유닛, "
                f"중단 기준 {pct}%·{threshold}유닛). 내일 UTC 자정 이후 재시도하거나 "
                f"EXTERNAL_API_DAILY_UNIT_LIMIT 를 조정하세요."
            )
            logger.warning("external_api_budget block label=%s %s", label, msg)
            raise ExternalApiBudgetExceeded(msg)

        _used_units += units
        if label:
            logger.info(
                "external_api_budget consume label=%s units=%s used=%s/%s soft=%s",
                label,
                units,
                _used_units,
                limit,
                threshold,
            )
