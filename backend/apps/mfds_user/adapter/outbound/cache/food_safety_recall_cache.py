"""?�품?�전?�라 ?�수·?�매중�?(I0490) ??06:00/15:00 KST 간격 ?�출·catalog 보�?."""

from __future__ import annotations

import json
import logging
import threading
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import urlopen
from zoneinfo import ZoneInfo

from matrix.grid_keymaker_secret_manager import get_keymaker
from mfds_user.adapter.outbound.cache.api_result import check_food_safety_api_result
from mfds_user.adapter.outbound.cache.catalog_merge import (
    CatalogMergeStats,
    merge_catalog_maps,
)

logger = logging.getLogger(__name__)

KST = ZoneInfo("Asia/Seoul")
SERVICE_ID = "I0490"
OPEN_API_BASE = "http://openapi.foodsafetykorea.go.kr/api"

def mfds_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"

CACHE_PATH = mfds_data_dir() / "recall_cache.json"
CATALOG_PATH = mfds_data_dir() / "recall_catalog.json"

_RECALL_CATALOG_FIELDS: tuple[str, ...] = (
    "product_name",
    "reason",
    "business_name",
    "registered_at",
    "recall_grade",
    "food_type",
    "serial_no",
)

def _recall_catalog_key(item: dict[str, str]) -> str:
    serial = (item.get("serial_no") or "").strip()
    if serial:
        return f"I0490|{serial}"
    return f"I0490|{item.get('product_name', '')}|{item.get('registered_at', '')}"

PAGE_SIZE = 1000
DISPLAY_LIMIT = 1
API_TIMEOUT_SEC = 20
MAX_FALLBACK_DAYS = 14
INDEX_WINDOW = 1000

_lock = threading.Lock()
_cached_items: list[dict[str, str]] = []
_cached_is_today: bool = False
_cached_matched_date: str | None = None
_last_fetched_at: datetime | None = None
_last_error: str | None = None

def _parse_cret_dt(value: str) -> datetime:
    raw = (value or "").strip()
    if not raw:
        return datetime.min.replace(tzinfo=KST)
    try:
        if "-" in raw and len(raw) >= 19:
            return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
        if raw[:8].isdigit():
            return datetime.strptime(raw[:8], "%Y%m%d").replace(tzinfo=KST)
    except ValueError:
        pass
    return datetime.min.replace(tzinfo=KST)

def _normalize_cached_items(raw: Any) -> list[dict[str, str]]:
    if not raw:
        return []
    if not isinstance(raw, list):
        return []

    out: list[dict[str, str]] = []
    for entry in raw:
        if isinstance(entry, dict) and entry.get("product_name"):
            out.append({k: str(entry.get(k) or "") for k in (
                "product_name", "reason", "business_name", "registered_at",
                "recall_grade", "food_type", "serial_no",
            )})
        elif isinstance(entry, list):
            out.extend(_normalize_cached_items(entry))
    return out

def _normalize_row(row: dict[str, Any]) -> dict[str, str]:
    return {
        "product_name": str(row.get("PRDTNM") or "").strip(),
        "reason": str(row.get("RTRVLPRVNS") or "").strip(),
        "business_name": str(row.get("BSSHNM") or "").strip(),
        "registered_at": str(row.get("CRET_DTM") or "").strip(),
        "recall_grade": str(row.get("RTRVL_GRDCD_NM") or "").strip(),
        "food_type": str(row.get("PRDLST_TYPE") or row.get("PRDLST_CD_NM") or "").strip(),
        "serial_no": str(row.get("RTRVLDSUSE_SEQ") or "").strip(),
    }

def _today_kst() -> date:
    return datetime.now(KST).date()

def _registered_date_kst(registered_at: str) -> date | None:
    dt = _parse_cret_dt(registered_at)
    if dt == datetime.min.replace(tzinfo=KST):
        return None
    return dt.date()

def _fetch_json_range(
    api_key: str,
    start_idx: int,
    end_idx: int,
    *,
    cret_dtm: str | None = None,
) -> dict[str, Any]:
    if start_idx < 1 or end_idx < start_idx:
        return {}
    url = f"{OPEN_API_BASE}/{api_key}/{SERVICE_ID}/json/{start_idx}/{end_idx}"
    if cret_dtm:
        url = f"{url}/CRET_DTM={cret_dtm}"
    try:
        with urlopen(url, timeout=API_TIMEOUT_SEC) as resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"?�품?�전?�라 API HTTP {e.code}: {body}") from e
    except URLError as e:
        raise RuntimeError(f"?�품?�전?�라 API ?�결 ?�패: {e.reason}") from e

def _fetch_rows_for_date(api_key: str, target_date: date) -> list[dict[str, Any]]:
    cret_dtm = target_date.strftime("%Y%m%d")
    collected: list[dict[str, Any]] = []
    start_idx = 1

    while True:
        end_idx = start_idx + PAGE_SIZE - 1
        payload = _fetch_json_range(api_key, start_idx, end_idx, cret_dtm=cret_dtm)
        rows, total = _extract_rows(payload)
        collected.extend(rows)
        if end_idx >= total or not rows:
            break
        start_idx = end_idx + 1

    return collected

def _extract_rows(payload: dict[str, Any]) -> tuple[list[dict[str, Any]], int]:
    block = payload.get(SERVICE_ID) or {}
    result = block.get("RESULT") or {}
    code = str(result.get("CODE", ""))
    msg = str(result.get("MSG", "API ?�류"))
    check_food_safety_api_result(code, msg)

    total = int(str(block.get("total_count") or "0"))
    row = block.get("row")
    if row is None:
        rows: list[dict[str, Any]] = []
    elif isinstance(row, list):
        rows = row
    else:
        rows = [row]
    return rows, total

def _rows_to_sorted_items(
    rows: list[dict[str, Any]],
    *,
    on_date: date | None = None,
) -> list[dict[str, str]]:
    normalized = [_normalize_row(r) for r in rows if isinstance(r, dict)]
    normalized = [r for r in normalized if r["product_name"]]
    if on_date is not None:
        normalized = [
            r for r in normalized if _registered_date_kst(r["registered_at"]) == on_date
        ]
    normalized.sort(key=lambda r: _parse_cret_dt(r["registered_at"]), reverse=True)
    return normalized

def _fetch_total_count(api_key: str) -> int:
    payload = _fetch_json_range(api_key, 1, 1)
    _, total = _extract_rows(payload)
    return total

def _fetch_latest_via_index_windows(api_key: str) -> list[dict[str, str]]:
    total = _fetch_total_count(api_key)
    if total <= 0:
        return []

    windows: list[tuple[int, int]] = [(1, min(INDEX_WINDOW, total))]
    if total > INDEX_WINDOW:
        windows.append((max(1, total - INDEX_WINDOW + 1), total))

    merged: dict[str, dict[str, str]] = {}
    for start_idx, end_idx in windows:
        payload = _fetch_json_range(api_key, start_idx, end_idx)
        rows, _ = _extract_rows(payload)
        for item in _rows_to_sorted_items(rows):
            key = item.get("serial_no") or f"{item['product_name']}|{item['registered_at']}"
            merged[key] = item

    ranked = sorted(merged.values(), key=lambda r: _parse_cret_dt(r["registered_at"]), reverse=True)
    return ranked

def load_stored_recall_catalog() -> list[dict[str, str]]:
    if not CATALOG_PATH.is_file():
        return []
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return _normalize_cached_items(data.get("items"))
    except Exception as e:
        logger.warning("recall catalog load failed: %s", e)
        return []

def save_stored_recall_catalog(
    items: list[dict[str, str]],
    *,
    wave: str,
    slot_display: str,
) -> None:
    CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": datetime.now(KST).isoformat(),
        "sync_wave": wave,
        "sync_slot": slot_display,
        "items": items,
    }
    CATALOG_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def sync_recall_catalog_from_api(*, wave: str, slot_display: str, max_items: int = 100) -> CatalogMergeStats:
    from mfds_user.adapter.outbound.cache.api_result import is_api_quota_blocked

    empty = CatalogMergeStats()
    if is_api_quota_blocked():
        logger.warning("recall catalog sync skipped: quota blocked")
        return empty
    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        return empty
    try:
        fetched = _fetch_latest_via_index_windows(api_key)[:max_items]
    except Exception as e:
        logger.warning("recall catalog index fetch failed: %s", e)
        return empty
    baseline: dict[str, dict[str, str]] = {
        _recall_catalog_key(item): item for item in load_stored_recall_catalog()
    }
    merged, stats = merge_catalog_maps(
        baseline,
        fetched,
        _recall_catalog_key,
        fields=_RECALL_CATALOG_FIELDS,
    )
    ranked = sorted(
        merged.values(),
        key=lambda r: _parse_cret_dt(r["registered_at"]),
        reverse=True,
    )
    save_stored_recall_catalog(ranked, wave=wave, slot_display=slot_display)
    logger.info(
        "recall catalog merge: added=%s updated=%s skipped=%s",
        stats.added,
        stats.updated,
        stats.skipped,
    )
    if ranked:
        best = ranked[0]
        matched = _registered_date_kst(best["registered_at"])
        today = _today_kst()
        global _cached_items, _cached_is_today, _cached_matched_date, _last_fetched_at, _last_error
        with _lock:
            _cached_items = [best]
            _cached_is_today = matched == today if matched else False
            _cached_matched_date = matched.isoformat() if matched else None
            _last_fetched_at = datetime.now(KST)
            _last_error = None
            _save_cache_file()
    return stats

def fetch_recall_catalog_for_sync(*, max_items: int = 100) -> list[dict[str, str]]:
    ranked = sorted(
        load_stored_recall_catalog(),
        key=lambda r: _parse_cret_dt(r["registered_at"]),
        reverse=True,
    )
    if ranked:
        return ranked[:max_items]
    items, _, _, _, _ = get_cached_recalls()
    return items[:max_items]

def fetch_recent_recall_items(*, max_days: int = 14, max_items: int = 80) -> list[dict[str, str]]:
    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        items, _, _, _, _ = get_cached_recalls()
        return items

    today = _today_kst()
    merged: dict[str, dict[str, str]] = {}
    for days_ago in range(max(1, max_days)):
        target = today - timedelta(days=days_ago)
        try:
            rows = _fetch_rows_for_date(api_key, target)
            for item in _rows_to_sorted_items(rows, on_date=target):
                key = item.get("serial_no") or f"{item['product_name']}|{item['registered_at']}"
                merged[key] = item
        except Exception as e:
            logger.warning("recall sync fetch %s failed: %s", target, e)
        if len(merged) >= max_items:
            break

    if merged:
        ranked = sorted(merged.values(), key=lambda r: _parse_cret_dt(r["registered_at"]), reverse=True)
        return ranked[:max_items]

    items, _, _, _, _ = get_cached_recalls()
    return items

def fetch_latest_recalls(*, limit: int = DISPLAY_LIMIT) -> tuple[list[dict[str, str]], bool, str | None]:
    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        raise RuntimeError("FOOD_SAFETY_API_KEY가 ?�정?��? ?�았?�니??")

    today = _today_kst()

    rows = _fetch_rows_for_date(api_key, today)
    today_items = _rows_to_sorted_items(rows, on_date=today)
    if today_items:
        return today_items[:limit], True, today.isoformat()

    for days_ago in range(1, MAX_FALLBACK_DAYS + 1):
        target = today - timedelta(days=days_ago)
        rows = _fetch_rows_for_date(api_key, target)
        day_items = _rows_to_sorted_items(rows, on_date=target)
        if day_items:
            return day_items[:limit], False, target.isoformat()

    index_items = _fetch_latest_via_index_windows(api_key)
    if index_items:
        best = index_items[0]
        matched = _registered_date_kst(best["registered_at"])
        return [best], False, (matched.isoformat() if matched else None)

    return [], False, None

def _save_cache_file() -> None:
    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "fetched_at": _last_fetched_at.isoformat() if _last_fetched_at else None,
        "error": _last_error,
        "is_today": _cached_is_today,
        "matched_date": _cached_matched_date,
        "items": _cached_items,
    }
    CACHE_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_cache_file() -> None:
    global _cached_items, _cached_is_today, _cached_matched_date, _last_fetched_at, _last_error
    if not CACHE_PATH.is_file():
        return
    try:
        data = json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        _cached_items = _normalize_cached_items(data.get("items"))
        _cached_is_today = bool(data.get("is_today", False))
        _cached_matched_date = data.get("matched_date")
        if not isinstance(_cached_matched_date, str):
            _cached_matched_date = None
        raw_at = data.get("fetched_at")
        _last_fetched_at = datetime.fromisoformat(raw_at).astimezone(KST) if raw_at else None
        _last_error = data.get("error")
    except Exception as e:
        logger.warning("recall cache load failed: %s", e)

def refresh_recall_cache(*, force: bool = False) -> list[dict[str, str]]:
    global _cached_items, _cached_is_today, _cached_matched_date, _last_fetched_at, _last_error

    with _lock:
        if (
            not force
            and _cached_items
            and all(isinstance(x, dict) for x in _cached_items)
            and _last_fetched_at
            and not should_refresh_now()
        ):
            return list(_cached_items)
        had_items = bool(_cached_items)

    try:
        items, is_today, matched_date = fetch_latest_recalls()
        fetch_error: str | None = None
    except Exception as e:
        fetch_error = str(e)
        logger.exception("recall fetch failed")
        items, is_today, matched_date = [], False, None
        if not had_items:
            raise

    with _lock:
        if fetch_error:
            _last_error = fetch_error
        else:
            _cached_items = items
            _cached_is_today = is_today
            _cached_matched_date = matched_date
            _last_fetched_at = datetime.now(KST)
            _last_error = None
        _save_cache_file()
        return list(_cached_items)

def get_cached_recalls() -> tuple[list[dict[str, str]], datetime | None, str | None, bool, str | None]:
    with _lock:
        if not _cached_items and CACHE_PATH.is_file():
            _load_cache_file()
        return list(_cached_items), _last_fetched_at, _last_error, _cached_is_today, _cached_matched_date

def should_refresh_now() -> bool:
    return False

normalize_recall_items_for_response = _normalize_cached_items

_load_cache_file()
