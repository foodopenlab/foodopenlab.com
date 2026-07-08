"""식품안전나라 식중독 원인물질별(I2850)/원인시설별(I2849) 통계 raw fetch."""

from __future__ import annotations

import json
import logging
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from matrix.grid_keymaker_secret_manager import get_keymaker
from mfds_user.adapter.outbound.cache.api_result import (
    check_food_safety_api_result,
    is_api_quota_blocked,
)

logger = logging.getLogger(__name__)

OPEN_API_BASE = "http://openapi.foodsafetykorea.go.kr/api"
SERVICE_AGENT = "I2850"
SERVICE_FACILITY = "I2849"
PAGE_SIZE = 1000
API_TIMEOUT_SEC = 20
MAX_ITEMS = 2000


def _fetch_json_range(api_key: str, service_id: str, start_idx: int, end_idx: int) -> dict[str, Any]:
    url = f"{OPEN_API_BASE}/{api_key}/{service_id}/json/{start_idx}/{end_idx}"
    try:
        with urlopen(url, timeout=API_TIMEOUT_SEC) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"식품안전나라 API HTTP {e.code}: {body}") from e
    except URLError as e:
        raise RuntimeError(f"식품안전나라 API 연결 실패: {e.reason}") from e


def _extract_rows(payload: dict[str, Any], service_id: str) -> tuple[list[dict[str, Any]], int]:
    block = payload.get(service_id) or {}
    result = block.get("RESULT") or {}
    check_food_safety_api_result(str(result.get("CODE", "")), str(result.get("MSG", "")))
    total = int(str(block.get("total_count") or "0"))
    row = block.get("row")
    if row is None:
        rows: list[dict[str, Any]] = []
    elif isinstance(row, list):
        rows = row
    else:
        rows = [row]
    return rows, total


def _fetch_all_rows(api_key: str, service_id: str, *, max_items: int = MAX_ITEMS) -> list[dict[str, Any]]:
    payload = _fetch_json_range(api_key, service_id, 1, 1)
    _, total = _extract_rows(payload, service_id)
    if total <= 0:
        return []

    collected: list[dict[str, Any]] = []
    start = 1
    limit = min(total, max_items)
    while start <= limit:
        end = min(start + PAGE_SIZE - 1, limit)
        payload = _fetch_json_range(api_key, service_id, start, end)
        rows, _ = _extract_rows(payload, service_id)
        collected.extend(rows)
        if not rows:
            break
        start = end + 1
    return collected


def _normalize_agent_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "category": "agent",
        "label": str(row.get("OCCRNC_VIRS") or "").strip() or "불명",
        "occurrence_year": str(row.get("OCCRNC_YEAR") or "").strip(),
        "occurrence_month": str(row.get("OCCRNC_MM") or "").strip(),
        "incident_count": str(row.get("OCCRNC_CNT") or "0").strip(),
        "patient_count": str(row.get("PATNT_CNT") or "0").strip(),
    }


def _normalize_facility_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "category": "facility",
        "label": str(row.get("OCCRNC_PLC") or "").strip() or "기타",
        "occurrence_year": str(row.get("OCCRNC_YEAR") or "").strip(),
        "occurrence_month": str(row.get("OCCRNC_MM") or "").strip(),
        "incident_count": str(row.get("OCCRNC_CNT") or "0").strip(),
        "patient_count": str(row.get("PATNT_CNT") or "0").strip(),
    }


def fetch_food_poisoning_stat_rows() -> list[dict[str, str]]:
    """식중독 원인물질별/원인시설별 raw row를 함께 가져온다. 실패 시 빈 목록."""
    if is_api_quota_blocked():
        logger.warning("food poisoning stat fetch skipped: quota blocked")
        return []

    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        return []

    rows: list[dict[str, str]] = []
    try:
        agent_raw = _fetch_all_rows(api_key, SERVICE_AGENT)
        rows.extend(_normalize_agent_row(r) for r in agent_raw if str(r.get("OCCRNC_YEAR") or "").strip())
    except Exception as e:
        logger.warning("food poisoning agent stat fetch failed: %s", e)

    try:
        facility_raw = _fetch_all_rows(api_key, SERVICE_FACILITY)
        rows.extend(_normalize_facility_row(r) for r in facility_raw if str(r.get("OCCRNC_YEAR") or "").strip())
    except Exception as e:
        logger.warning("food poisoning facility stat fetch failed: %s", e)

    return rows
