"""식품안전나라 행정처분(I0470·I0480·I0481) — 09:40/17:40 KST 간격 호출·catalog 보관."""

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
from mfds_user.adapter.outbound.cache.api_result import (
    check_food_safety_api_result,
    is_api_quota_blocked,
)
from mfds_user.adapter.outbound.cache.catalog_merge import (
    CatalogMergeStats,
    merge_catalog_maps,
)

logger = logging.getLogger(__name__)

KST = ZoneInfo("Asia/Seoul")
SANCTION_SERVICES: tuple[tuple[str, str], ...] = (
    ("I0470", "행정처분"),
    ("I0480", "제조가공업"),
    ("I0481", "식품판매업"),
)
OPEN_API_BASE = "http://openapi.foodsafetykorea.go.kr/api"

def mfds_data_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "data"

CACHE_PATH = mfds_data_dir() / "sanction_cache.json"
CATALOG_PATH = mfds_data_dir() / "sanction_catalog.json"

_SANCTION_CATALOG_FIELDS: tuple[str, ...] = (
    "business_name",
    "industry",
    "disposition_date",
    "disposition_start",
    "disposition_type",
    "violation",
    "address",
    "representative",
    "disposition_detail",
    "agency",
    "serial_no",
    "category",
    "service_id",
)
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

_enrich_running: bool = False

def is_enrich_running() -> bool:
    return _enrich_running

def set_enrich_running(val: bool) -> None:
    global _enrich_running
    _enrich_running = val

def _parse_dsps_dt(value: str) -> datetime:
    raw = (value or "").strip()
    if not raw:
        return datetime.min.replace(tzinfo=KST)
    if "-" in raw and len(raw) >= 19:
        try:
            return datetime.strptime(raw[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=KST)
        except ValueError:
            pass
    if "-" in raw and len(raw) >= 10:
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").replace(tzinfo=KST)
        except ValueError:
            pass
    digits = "".join(c for c in raw if c.isdigit())
    try:
        if len(digits) >= 14:
            return datetime.strptime(digits[:14], "%Y%m%d%H%M%S").replace(tzinfo=KST)
        if len(digits) >= 8:
            return datetime.strptime(digits[:8], "%Y%m%d").replace(tzinfo=KST)
    except ValueError:
        pass
    return datetime.min.replace(tzinfo=KST)

def _sanction_display_metric(r: dict[str, str]) -> tuple[float, float, int]:
    sentinel = datetime.min.replace(tzinfo=KST)
    disp = _parse_dsps_dt(r.get("disposition_date") or "")
    if disp == sentinel:
        disp_ts = float("-inf")
    else:
        disp_ts = disp.timestamp()
    bg_raw = (r.get("disposition_start") or "").strip()
    if bg_raw:
        bg_dt = _parse_dsps_dt(bg_raw)
        bg_ts = float("inf") if bg_dt == sentinel else bg_dt.timestamp()
    else:
        bg_ts = float("inf")
    sn = (r.get("serial_no") or "").strip()
    seq = int(sn) if sn.isdigit() else 10**18
    return (-disp_ts, bg_ts, seq)

def _normalize_cached_items(raw: Any) -> list[dict[str, str]]:
    if not raw:
        return []
    if not isinstance(raw, list):
        return []

    out: list[dict[str, str]] = []
    for entry in raw:
        if isinstance(entry, dict) and entry.get("business_name"):
            out.append({k: str(entry.get(k) or "") for k in (
                "business_name", "industry", "disposition_date", "disposition_start",
                "disposition_type",
                "violation", "address", "representative", "disposition_detail",
                "agency", "serial_no", "category", "service_id",
            )})
        elif isinstance(entry, list):
            out.extend(_normalize_cached_items(entry))
    return out

def _normalize_row(row: dict[str, Any], *, category: str, service_id: str) -> dict[str, str]:
    return {
        "business_name": str(row.get("PRCSCITYPOINT_BSSHNM") or "").strip(),
        "industry": str(row.get("INDUTY_CD_NM") or "").strip(),
        "disposition_date": str(row.get("DSPS_DCSNDT") or "").strip(),
        "disposition_start": str(row.get("DSPS_BGNDT") or "").strip(),
        "disposition_type": str(row.get("DSPS_TYPECD_NM") or "").strip(),
        "violation": str(row.get("VILTCN") or "").strip(),
        "address": str(row.get("ADDR") or "").strip(),
        "representative": str(row.get("PRSDNT_NM") or "").strip(),
        "disposition_detail": str(row.get("DSPSCN") or "").strip(),
        "agency": str(row.get("DSPS_INSTTCD_NM") or "").strip(),
        "serial_no": str(row.get("DSPSDTLS_SEQ") or "").strip(),
        "category": category,
        "service_id": service_id,
    }

def _today_kst() -> date:
    return datetime.now(KST).date()

def _disposition_date_kst(disposition_date: str) -> date | None:
    dt = _parse_dsps_dt(disposition_date)
    if dt == datetime.min.replace(tzinfo=KST):
        return None
    return dt.date()

def _fetch_json_range(
    api_key: str,
    service_id: str,
    start_idx: int,
    end_idx: int,
    *,
    dsps_dcsndt: str | None = None,
) -> dict[str, Any]:
    if start_idx < 1 or end_idx < start_idx:
        return {}
    url = f"{OPEN_API_BASE}/{api_key}/{service_id}/json/{start_idx}/{end_idx}"
    if dsps_dcsndt:
        url = f"{url}/DSPS_DCSNDT={dsps_dcsndt}"
    try:
        with urlopen(url, timeout=API_TIMEOUT_SEC) as resp:
            raw = resp.read().decode(errors="replace")
    except HTTPError as e:
        body = e.read().decode(errors="replace")[:200]
        raise RuntimeError(f"?�품?�전?�라 API HTTP {e.code}: {body}") from e
    except URLError as e:
        raise RuntimeError(f"?�품?�전?�라 API ?�결 ?�패: {e.reason}") from e

    if "인증키" in raw or raw.strip().startswith("<"):
        raise RuntimeError(
            f"FOOD_SAFETY_API_KEY가 행정처분({service_id}) API에 인증되지 않았습니다. "
            "식품안전나라 OpenAPI에서 해당 서비스 사용신청·인증을 확인해 주세요."
        )
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError("?�품?�전?�라 API ?�답 ?�식???�바르�? ?�습?�다.") from e

def _extract_rows(payload: dict[str, Any], service_id: str) -> tuple[list[dict[str, Any]], int]:
    block = payload.get(service_id) or {}
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

def _fetch_rows_for_date(
    api_key: str,
    service_id: str,
    target_date: date,
) -> list[dict[str, Any]]:
    dsps_dcsndt = target_date.strftime("%Y%m%d")
    collected: list[dict[str, Any]] = []
    start_idx = 1

    while True:
        end_idx = start_idx + PAGE_SIZE - 1
        payload = _fetch_json_range(
            api_key, service_id, start_idx, end_idx, dsps_dcsndt=dsps_dcsndt,
        )
        rows, total = _extract_rows(payload, service_id)
        collected.extend(rows)
        if end_idx >= total or not rows:
            break
        start_idx = end_idx + 1

    return collected

def _rows_to_sorted_items(
    rows: list[dict[str, Any]],
    *,
    category: str,
    service_id: str,
    on_date: date | None = None,
) -> list[dict[str, str]]:
    normalized = [
        _normalize_row(r, category=category, service_id=service_id)
        for r in rows
        if isinstance(r, dict)
    ]
    normalized = [r for r in normalized if r["business_name"]]
    if on_date is not None:
        normalized = [
            r for r in normalized if _disposition_date_kst(r["disposition_date"]) == on_date
        ]
    normalized.sort(key=_sanction_display_metric)
    return normalized

def _pick_latest(items: list[dict[str, str]], *, limit: int) -> list[dict[str, str]]:
    ranked = sorted(items, key=_sanction_display_metric)
    return ranked[:limit]

def _fetch_total_count(api_key: str, service_id: str) -> int:
    payload = _fetch_json_range(api_key, service_id, 1, 1)
    _, total = _extract_rows(payload, service_id)
    return total

def _fetch_latest_via_index_windows(
    api_key: str,
    service_id: str,
    category: str,
) -> list[dict[str, str]]:
    total = _fetch_total_count(api_key, service_id)
    if total <= 0:
        return []

    windows: list[tuple[int, int]] = [(1, min(INDEX_WINDOW, total))]
    if total > INDEX_WINDOW:
        windows.append((max(1, total - INDEX_WINDOW + 1), total))

    merged: dict[str, dict[str, str]] = {}
    for start_idx, end_idx in windows:
        payload = _fetch_json_range(api_key, service_id, start_idx, end_idx)
        rows, _ = _extract_rows(payload, service_id)
        for item in _rows_to_sorted_items(rows, category=category, service_id=service_id):
            key = f"{service_id}|{item.get('serial_no') or item['business_name']}|{item['disposition_date']}"
            merged[key] = item

    return sorted(merged.values(), key=_sanction_display_metric)

def _collect_for_date(
    api_key: str,
    target_date: date,
    *,
    on_date: date | None,
) -> list[dict[str, str]]:
    merged: list[dict[str, str]] = []
    errors: list[str] = []

    for service_id, category in SANCTION_SERVICES:
        try:
            rows = _fetch_rows_for_date(api_key, service_id, target_date)
            merged.extend(
                _rows_to_sorted_items(
                    rows,
                    category=category,
                    service_id=service_id,
                    on_date=on_date,
                )
            )
        except Exception as e:
            errors.append(f"{service_id}: {e}")
            logger.warning("sanction fetch %s for %s failed: %s", service_id, target_date, e)

    if not merged and errors:
        raise RuntimeError("; ".join(errors))
    return merged

def _catalog_item_key(item: dict[str, str]) -> str:
    return (
        f"{item.get('service_id')}|{item.get('serial_no') or ''}|"
        f"{item['business_name']}|{item['disposition_date']}"
    )

def load_stored_sanction_catalog() -> list[dict[str, str]]:
    if not CATALOG_PATH.is_file():
        return []
    try:
        data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
        return _normalize_cached_items(data.get("items"))
    except Exception as e:
        logger.warning("sanction catalog load failed: %s", e)
        return []

def save_stored_sanction_catalog(
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

def sync_sanction_service_to_catalog(service_id: str, category: str) -> CatalogMergeStats:
    empty = CatalogMergeStats()
    if is_api_quota_blocked():
        logger.warning("sanction sync %s skipped: quota blocked", service_id)
        return empty
    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        return empty
    try:
        fetched = _fetch_latest_via_index_windows(api_key, service_id, category)
    except Exception as e:
        logger.warning("sanction catalog index %s failed: %s", service_id, e)
        return empty
    baseline: dict[str, dict[str, str]] = {
        _catalog_item_key(item): item for item in load_stored_sanction_catalog()
    }
    merged, stats = merge_catalog_maps(
        baseline,
        fetched,
        _catalog_item_key,
        fields=_SANCTION_CATALOG_FIELDS,
    )
    ranked = sorted(merged.values(), key=_sanction_display_metric)
    save_stored_sanction_catalog(ranked, wave=_active_sync_wave(), slot_display=_active_sync_slot())
    logger.info(
        "sanction catalog merge %s: added=%s updated=%s skipped=%s",
        service_id,
        stats.added,
        stats.updated,
        stats.skipped,
    )
    return stats

_active_wave: str = ""
_active_slot: str = ""

def set_active_sync_context(*, wave: str, slot_display: str) -> None:
    global _active_wave, _active_slot
    _active_wave = wave
    _active_slot = slot_display

def _active_sync_wave() -> str:
    return _active_wave

def _active_sync_slot() -> str:
    return _active_slot

def finalize_sanction_latest_from_catalog() -> None:
    global _cached_items, _cached_is_today, _cached_matched_date, _last_fetched_at, _last_error
    ranked = load_stored_sanction_catalog()
    if not ranked:
        return
    best = ranked[0]
    matched = _disposition_date_kst(best["disposition_date"])
    today = _today_kst()
    with _lock:
        _cached_items = [best]
        _cached_is_today = matched == today if matched else False
        _cached_matched_date = matched.isoformat() if matched else None
        _last_fetched_at = datetime.now(KST)
        _last_error = None
        _save_cache_file()

def fetch_sanction_catalog_for_sync(*, max_items: int = 100) -> list[dict[str, str]]:
    ranked = sorted(load_stored_sanction_catalog(), key=_sanction_display_metric)
    if ranked:
        return ranked[:max_items]
    items, _, _, _, _ = get_cached_sanctions()
    return items[:max_items]

def fetch_recent_sanction_items(*, max_days: int = 14, max_items: int = 80) -> list[dict[str, str]]:
    if is_api_quota_blocked():
        items, _, _, _, _ = get_cached_sanctions()
        return items[:max_items]

    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        items, _, _, _, _ = get_cached_sanctions()
        return items

    today = _today_kst()
    merged: dict[str, dict[str, str]] = {}
    for days_ago in range(max(1, max_days)):
        target = today - timedelta(days=days_ago)
        try:
            for item in _collect_for_date(api_key, target, on_date=target):
                key = f"{item.get('service_id')}|{item.get('serial_no')}|{item['business_name']}|{item['disposition_date']}"
                merged[key] = item
        except Exception as e:
            logger.warning("sanction sync fetch %s failed: %s", target, e)
        if len(merged) >= max_items:
            break

    if merged:
        ranked = sorted(merged.values(), key=_sanction_display_metric)
        return ranked[:max_items]

    items, _, _, _, _ = get_cached_sanctions()
    return items

def fetch_latest_sanctions(*, limit: int = DISPLAY_LIMIT) -> tuple[list[dict[str, str]], bool, str | None]:
    keymaker = get_keymaker()
    api_key = keymaker.get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        raise RuntimeError("FOOD_SAFETY_API_KEY가 ?�정?��? ?�았?�니??")

    today = _today_kst()

    today_items = _collect_for_date(api_key, today, on_date=today)
    if today_items:
        return _pick_latest(today_items, limit=limit), True, today.isoformat()

    for days_ago in range(1, MAX_FALLBACK_DAYS + 1):
        target = today - timedelta(days=days_ago)
        day_items = _collect_for_date(api_key, target, on_date=target)
        if day_items:
            return _pick_latest(day_items, limit=limit), False, target.isoformat()

    index_items: list[dict[str, str]] = []
    index_errors: list[str] = []
    for service_id, category in SANCTION_SERVICES:
        try:
            index_items.extend(_fetch_latest_via_index_windows(api_key, service_id, category))
        except Exception as e:
            index_errors.append(f"{service_id}: {e}")
            logger.warning("sanction index fetch %s failed: %s", service_id, e)

    if index_items:
        best = _pick_latest(index_items, limit=1)[0]
        matched = _disposition_date_kst(best["disposition_date"])
        return [best], False, (matched.isoformat() if matched else None)

    if index_errors:
        raise RuntimeError("; ".join(index_errors))

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
        logger.warning("sanction cache load failed: %s", e)

def refresh_sanction_cache(*, force: bool = False) -> list[dict[str, str]]:
    global _cached_items, _cached_is_today, _cached_matched_date, _last_fetched_at, _last_error

    if is_api_quota_blocked() and not force:
        with _lock:
            return list(_cached_items)

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
        items, is_today, matched_date = fetch_latest_sanctions()
        fetch_error: str | None = None
    except Exception as e:
        fetch_error = str(e)
        logger.exception("sanction fetch failed")
        items, is_today, matched_date = [], False, None
        if not had_items:
            raise

    with _lock:
        if fetch_error:
            _last_error = fetch_error
            if not had_items:
                _cached_items = []
        elif items:
            _cached_items = items
            _cached_is_today = is_today
            _cached_matched_date = matched_date
            _last_fetched_at = datetime.now(KST)
            _last_error = None
        else:
            _last_error = fetch_error or "?�정처분 API ?�답??비어 ?�습?�다."
        _save_cache_file()
        return list(_cached_items)

def get_cached_sanctions() -> tuple[list[dict[str, str]], datetime | None, str | None, bool, str | None]:
    with _lock:
        if not _cached_items and CACHE_PATH.is_file():
            _load_cache_file()
        return list(_cached_items), _last_fetched_at, _last_error, _cached_is_today, _cached_matched_date

def should_refresh_now() -> bool:
    return False

normalize_sanction_items_for_response = _normalize_cached_items

_load_cache_file()
