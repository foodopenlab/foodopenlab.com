"""식품안전나라 HACCP 지정현황(I0580/I0610) → DB 캐시 동기화."""

from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional, cast
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from sqlalchemy import desc, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from matrix.grid_keymaker_secret_manager import get_keymaker
from mfds_user.adapter.outbound.cache.catalog_merge import raw_json_fingerprint
from mfds_user.adapter.outbound.orm.haccp_certification_orm import HaccpCertificationModel

logger = logging.getLogger(__name__)

OPEN_API_BASE = "http://openapi.foodsafetykorea.go.kr/api"
HACCP_SERVICE_IDS = ("I0580", "I0610")
PAGE_SIZE = 1000
MAX_ITEMS_PER_SERVICE = 50_000
API_TIMEOUT_SEC = 20
PAGE_RETRY_COUNT = 2

@dataclass
class HaccpFetchResult:
    rows: list[dict[str, Any]]
    completed_service_ids: tuple[str, ...]


@dataclass(frozen=True)
class HaccpSyncStats:
    inserted: int = 0
    updated: int = 0
    skipped: int = 0

    @property
    def touched(self) -> int:
        return self.inserted + self.updated

def _normalize_business_name(value: str | None) -> str:
    text = (value or "").lower()
    for token in ("주식회사", "(주)", "㈜"):
        text = text.replace(token, "")
    return re.sub(r"[\s().\-_/]+", "", text)

def _digits_only(value: str | None) -> str:
    return re.sub(r"\D+", "", value or "")

def _haccp_cache_id(row: dict[str, Any]) -> str:
    sid = row["service_id"]
    appn = (row.get("haccp_appn_no") or "").strip()
    lic = _digits_only(row.get("license_number"))
    product = _normalize_business_name(row.get("product_name"))
    if appn:
        return f"{sid}:{appn}:{lic}:{product}"
    return f"{sid}:{lic}:{product or _normalize_business_name(row.get('business_name'))}"

def _text(row: dict[str, Any], key: str) -> str:
    return str(row.get(key) or "").strip()

def _is_active(row: dict[str, Any]) -> bool:
    closed = _text(row, "CLSBIZ_DT")
    returned = _text(row, "CRTFC_RETN_DT")
    status = _text(row, "CLSBIZ_DVS_CD_NM")
    return not (closed or returned or "폐업" in status)

def _row_to_cache_dict(service_id: str, row: dict[str, Any]) -> dict[str, Any] | None:
    business_name = _text(row, "BSSH_NM")
    license_number = _digits_only(_text(row, "LCNS_NO"))
    haccp_no = _text(row, "HACCP_APPN_NO")
    product_name = _text(row, "PRDLST_NM")
    if not business_name or not (license_number or haccp_no or product_name):
        return None
    return {
        "service_id": service_id,
        "business_name": business_name,
        "license_number": license_number,
        "haccp_appn_no": haccp_no,
        "designated_date": _text(row, "HACCP_APPN_DT"),
        "expiry_date": _text(row, "CRTFC_ENDDT"),
        "cancelled_date": _text(row, "ASGN_CANCL_DT"),
        "returned_date": _text(row, "CRTFC_RETN_DT"),
        "product_name": product_name,
        "industry_name": _text(row, "INDUTY_CD_NM"),
        "representative_name": _text(row, "PRSDNT_NM"),
        "address": _text(row, "SITE_ADDR"),
        "business_status": _text(row, "CLSBIZ_DVS_CD_NM"),
        "is_active": "1" if _is_active(row) else "0",
        "raw_json_dict": dict(row),
    }


def _row_to_model_data(row: dict[str, Any], *, now: datetime, sync_started_at: datetime) -> dict[str, Any]:
    return {
        "service_id": row["service_id"],
        "business_name": row["business_name"],
        "normalized_business_name": _normalize_business_name(row["business_name"]),
        "license_number": _digits_only(row.get("license_number")),
        "haccp_appn_no": (row.get("haccp_appn_no") or "").strip() or None,
        "designated_date": (row.get("designated_date") or "").strip() or None,
        "expiry_date": (row.get("expiry_date") or "").strip() or None,
        "cancelled_date": (row.get("cancelled_date") or "").strip() or None,
        "returned_date": (row.get("returned_date") or "").strip() or None,
        "product_name": (row.get("product_name") or "").strip() or None,
        "industry_name": (row.get("industry_name") or "").strip() or None,
        "representative_name": (row.get("representative_name") or "").strip() or None,
        "address": (row.get("address") or "").strip() or None,
        "business_status": (row.get("business_status") or "").strip() or None,
        "is_active": row.get("is_active") == "1",
        "raw_json": row.get("raw_json_dict") or {},
        "fetched_at": now,
        "last_seen_at": sync_started_at,
    }

def _fetch_json_range(api_key: str, service_id: str, start_idx: int, end_idx: int) -> tuple[list[dict[str, Any]], int]:
    url = f"{OPEN_API_BASE}/{api_key}/{service_id}/json/{start_idx}/{end_idx}"
    try:
        with urlopen(url, timeout=API_TIMEOUT_SEC) as resp:
            body = resp.read()
            charset = resp.headers.get_content_charset()
    except (HTTPError, URLError, OSError) as e:
        raise RuntimeError(f"{service_id} HACCP API 연결 실패: {e}") from e

    raw = _decode_response_body(body, charset)
    if raw.lstrip().startswith("<"):
        raise RuntimeError(f"{service_id} HACCP API가 JSON 대신 HTML 응답을 반환했습니다.")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"{service_id} HACCP API JSON 파싱 실패") from e

    block = payload.get(service_id) or {}
    result = block.get("RESULT") or {}
    code = str(result.get("CODE") or "")
    if code and not code.startswith("INFO"):
        raise RuntimeError(f"{service_id} HACCP API 오류 {code}: {result.get('MSG')}")

    total = int(str(block.get("total_count") or "0"))
    row = block.get("row")
    if row is None:
        return [], total
    rows = row if isinstance(row, list) else [row]
    return [r for r in rows if isinstance(r, dict)], total

def _decode_response_body(body: bytes, charset: str | None) -> str:
    encodings = [charset, "utf-8", "cp949", "euc-kr"]
    for enc in [e for e in encodings if e]:
        try:
            return body.decode(enc)
        except UnicodeDecodeError:
            continue
    return body.decode("utf-8", errors="replace")

def _fetch_json_range_with_retry(api_key: str, service_id: str, start_idx: int, end_idx: int) -> tuple[list[dict[str, Any]], int]:
    last_error: Exception | None = None
    for attempt in range(1, PAGE_RETRY_COUNT + 1):
        try:
            return _fetch_json_range(api_key, service_id, start_idx, end_idx)
        except Exception as e:
            last_error = e
            logger.warning(
                "HACCP API fetch retry service=%s range=%s-%s attempt=%s/%s: %s",
                service_id,
                start_idx,
                end_idx,
                attempt,
                PAGE_RETRY_COUNT,
                e,
            )
    raise RuntimeError(f"{service_id} HACCP API range {start_idx}-{end_idx} failed") from last_error

def fetch_haccp_certification_rows_for_sync(*, max_items_per_service: int = MAX_ITEMS_PER_SERVICE) -> HaccpFetchResult:
    api_key = get_keymaker().get_secret("FOOD_SAFETY_API_KEY")
    if not api_key:
        logger.warning("FOOD_SAFETY_API_KEY 미설정 — HACCP 인증 캐시 동기화 생략")
        return HaccpFetchResult(rows=[], completed_service_ids=())

    out: list[dict[str, Any]] = []
    completed: list[str] = []
    for service_id in HACCP_SERVICE_IDS:
        start = 1
        service_count = 0
        completed_service = False
        while service_count < max_items_per_service:
            end = start + PAGE_SIZE - 1
            try:
                rows, _ = _fetch_json_range_with_retry(api_key, service_id, start, end)
            except Exception as e:
                logger.warning("HACCP %s sync stopped at range %s-%s: %s", service_id, start, end, e)
                break
            for row in rows:
                mapped = _row_to_cache_dict(service_id, row)
                if mapped is not None:
                    out.append(mapped)
                    service_count += 1
            if not rows or len(rows) < PAGE_SIZE:
                completed_service = True
                break
            start = end + 1
        if completed_service:
            completed.append(service_id)
        logger.info("fetched HACCP %s rows=%s", service_id, service_count)
    return HaccpFetchResult(rows=out, completed_service_ids=tuple(completed))

async def sync_haccp_certifications_to_db(
    session: AsyncSession,
    *,
    max_items_per_service: int = MAX_ITEMS_PER_SERVICE,
) -> HaccpSyncStats:
    sync_started_at = datetime.utcnow()
    result = await asyncio.to_thread(
        fetch_haccp_certification_rows_for_sync,
        max_items_per_service=max_items_per_service,
    )
    rows = result.rows
    if not rows:
        return HaccpSyncStats()

    now = datetime.utcnow()
    rows_by_id = {_haccp_cache_id(row): row for row in rows}
    rows = list(rows_by_id.values())
    ids = list(rows_by_id.keys())

    inserted = 0
    updated = 0
    skipped = 0
    chunk_size = 1000
    for chunk_start in range(0, len(rows), chunk_size):
        chunk_rows = rows[chunk_start : chunk_start + chunk_size]
        chunk_ids = ids[chunk_start : chunk_start + chunk_size]
        chunk_touched = False

        existing_map: dict[str, HaccpCertificationModel] = {}
        for i in range(0, len(chunk_ids), 1000):
            stmt = select(HaccpCertificationModel).where(
                cast(Any, HaccpCertificationModel.id).in_(chunk_ids[i : i + 1000])
            )
            res = await session.execute(stmt)
            existing_map.update({row.id: row for row in res.scalars().all()})

        for row in chunk_rows:
            cert_id = _haccp_cache_id(row)
            existing = existing_map.get(cert_id)
            raw_dict = row.get("raw_json_dict") or {}
            new_fp = raw_json_fingerprint(raw_dict)

            if existing is not None:
                old_raw = existing.raw_json if isinstance(existing.raw_json, dict) else {}
                if raw_json_fingerprint(old_raw) == new_fp:
                    skipped += 1
                    continue
                data = _row_to_model_data(row, now=now, sync_started_at=sync_started_at)
                for key, value in data.items():
                    setattr(existing, key, value)
                updated += 1
                chunk_touched = True
            else:
                data = _row_to_model_data(row, now=now, sync_started_at=sync_started_at)
                session.add(HaccpCertificationModel(id=cert_id, **data))
                inserted += 1
                chunk_touched = True

        if chunk_touched:
            await session.commit()
        session.expunge_all()
        logger.info(
            "haccp_certifications_cache merge progress inserted=%s updated=%s skipped=%s processed=%s/%s",
            inserted,
            updated,
            skipped,
            min(chunk_start + chunk_size, len(rows)),
            len(rows),
        )

    for i in range(0, len(ids), 1000):
        await session.execute(
            update(HaccpCertificationModel)
            .where(cast(Any, HaccpCertificationModel.id).in_(ids[i : i + 1000]))
            .values(last_seen_at=sync_started_at)
        )
    await session.commit()
    session.expunge_all()

    if result.completed_service_ids:
        stmt_update = (
            update(HaccpCertificationModel)
            .where(cast(Any, HaccpCertificationModel.service_id).in_(result.completed_service_ids))
            .where(cast(Any, HaccpCertificationModel.last_seen_at) < sync_started_at)
            .values(is_active=False, fetched_at=datetime.utcnow())
        )
        res_update = await session.execute(stmt_update)
        await session.commit()
        inactive = int(cast(Any, res_update).rowcount or 0)
        if inactive:
            logger.info("marked inactive HACCP rows=%s", inactive)

    logger.info(
        "haccp_certifications_cache upsert_many inserted=%s updated=%s skipped=%s",
        inserted,
        updated,
        skipped,
    )
    return HaccpSyncStats(inserted=inserted, updated=updated, skipped=skipped)

