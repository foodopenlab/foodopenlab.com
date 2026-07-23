"""식약처(식품안전나라 OpenAPI + www.mfds.go.kr) 외부 호출 긴급 침묵 게이트.

차단 대응 등으로 일정 기간 모든 아웃바운드 호출을 정지시킨다.

- `data/mfds_silence.json` 의 `until`(ISO, KST) 시각까지 `is_mfds_silenced()` 가 True.
- 파일 기반이라 실행 중인 프로세스도 다음 호출 시점에 즉시 반영되고, 재시작에도 유지된다.
- 만료 시각이 지나면 자동으로 해제된다(파일이 남아 있어도 False).
- 기존 OpenAPI 쿼터차단(`api_result`)과 독립적이라, 수동 sync 의 quota clear 로도 풀리지 않는다.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)
KST = ZoneInfo("Asia/Seoul")


def _silence_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "mfds_silence.json"


def silenced_until() -> datetime | None:
    path = _silence_path()
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        raw = data.get("until")
        if not raw:
            return None
        return datetime.fromisoformat(raw).astimezone(KST)
    except Exception as e:
        logger.warning("mfds silence read failed: %s", e)
        return None


def is_mfds_silenced() -> bool:
    until = silenced_until()
    if until is None:
        return False
    return datetime.now(KST) < until


def arm_mfds_silence(hours: float = 72.0, *, reason: str = "") -> datetime:
    now = datetime.now(KST)
    until = now + timedelta(hours=hours)
    path = _silence_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "armed_at": now.isoformat(),
                "until": until.isoformat(),
                "hours": hours,
                "reason": reason,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    logger.warning("MFDS outbound calls SILENCED until %s (%s)", until.isoformat(), reason or "-")
    return until


def clear_mfds_silence() -> None:
    path = _silence_path()
    if path.is_file():
        path.unlink()
        logger.warning("MFDS outbound silence CLEARED")
