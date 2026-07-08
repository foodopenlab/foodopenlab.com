"""식품안전나라 JSON 캐시 → PostgreSQL recalls_cache / enforcement_cache 동기화."""

from __future__ import annotations

import asyncio
import logging
import re
import json
from datetime import datetime
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from mfds_user.adapter.outbound.orm.recall_orm import RecallModel
from mfds_user.adapter.outbound.orm.enforcement_orm import EnforcementModel
from mfds_user.adapter.inbound.api.schemas.recall_schema import RecallSchema
from mfds_user.adapter.inbound.api.schemas.enforcement_schema import EnforcementSchema

logger = logging.getLogger(__name__)

# --- 카테고리 매핑 및 필터 헬퍼 ---
PROCESS_TYPE_LABELS = ("영업정지", "영업취소", "과징금", "시정명령")

def _map_food_category(food_type: str) -> str:
    t = (food_type or "").strip()
    if not t:
        return "기타"
    if "수입" in t:
        return "수입식품"
    if "식육" in t or "육류" in t:
        return "식육가공품"
    if "곡" in t:
        return "곡류가공품"
    if "조미" in t:
        return "조미식품"
    if "건강" in t or "간편" in t:
        return "건강간편식"
    if "당" in t or "잼" in t or "과자" in t or "빵" in t:
        return "당류가공품"
    if "유" in t or "가공" in t or "유가" in t or "유제품" in t:
        return "유가공품"
    return t

def _map_process_type(raw: str | None) -> str:
    s = (raw or "").strip()
    if not s:
        return "기타"
    for label in PROCESS_TYPE_LABELS:
        if label in s or s == label:
            return label
    return "기타"


_DETAIL_PROCESS_TYPE_LABELS: tuple[str, ...] = (
    # 처분내용(DSPSCN)에는 복합 문자열이 섞일 수 있어, UI 필터(영업취소/시정명령)를 우선 노출한다.
    "영업취소",
    "시정명령",
    "과징금",
    "영업정지",
)


def _map_process_type_from_detail(raw: str | None) -> str:
    s = (raw or "").strip()
    if not s:
        return "기타"
    for label in _DETAIL_PROCESS_TYPE_LABELS:
        if label in s or s == label:
            return label
    return "기타"

def _parse_recall_grade(raw: str) -> int | None:
    s = (raw or "").strip()
    m = re.search(r"([123])", s)
    if m:
        return int(m.group(1))
    return None

def _raw_json_fingerprint(raw: dict) -> str:
    return json.dumps(raw, sort_keys=True, ensure_ascii=False, default=str)

def _recall_row_to_schema(row: dict[str, str]) -> RecallSchema | None:
    serial = (row.get("serial_no") or "").strip()
    product = (row.get("product_name") or "").strip()
    if not product:
        return None
    rid = serial or f"recall-{product[:40]}-{row.get('registered_at', '')}"
    food_type = (row.get("food_type") or "").strip()
    return RecallSchema(
        id=rid,
        product_name=product,
        manufacturer=(row.get("business_name") or "").strip() or "미상",
        food_type=food_type or None,
        food_category=_map_food_category(food_type),
        recall_reason=(row.get("reason") or "").strip() or None,
        recall_grade=_parse_recall_grade(row.get("recall_grade") or ""),
        recall_method=None,
        registered_at=(row.get("registered_at") or "").strip() or None,
        image_url=None,
    )

def _sanction_row_to_schema(row: dict[str, str]) -> EnforcementSchema | None:
    serial = (row.get("serial_no") or "").strip()
    business = (row.get("business_name") or "").strip()
    if not business:
        return None
    sid = (row.get("service_id") or "I0470").strip()
    eid = f"{sid}-{serial}" if serial else f"{sid}-{business[:30]}-{row.get('disposition_date', '')}"
    raw_type = (row.get("disposition_type") or "").strip()
    raw_detail = (row.get("disposition_detail") or "").strip()
    mapped_type = _map_process_type(raw_type) if raw_type else "기타"
    detail_type = _map_process_type_from_detail(raw_detail)
    # 처분유형이 "영업정지"로 내려오더라도 처분내용에 "시정명령/영업취소"가 명시되는 케이스가 있어
    # UI 필터에서 조회 가능하도록 detail 기반 타입을 우선한다.
    if detail_type in {"영업취소", "시정명령"}:
        mapped_type = detail_type

    return EnforcementSchema(
        id=eid,
        business_name=business,
        business_type=(row.get("industry") or "").strip() or None,
        address=(row.get("address") or "").strip() or None,
        process_type=mapped_type,
        violation_content=(row.get("violation") or "").strip() or None,
        violation_date=(row.get("disposition_start") or row.get("disposition_date") or "").strip() or None,
        process_date=(row.get("disposition_date") or "").strip() or None,
        district=(row.get("agency") or "").strip() or None,
    )

# --- 로드 및 동기화 구현 ---

def _load_recall_rows_sync(*, allow_api_fetch: bool = True) -> list[dict[str, str]]:
    from mfds_user.adapter.outbound.cache.food_safety_recall_cache import (
        fetch_recent_recall_items,
        get_cached_recalls,
    )
    items, _, _, _, _ = get_cached_recalls()
    if not allow_api_fetch:
        return items
    if len(items) >= 5:
        return items
    try:
        return fetch_recent_recall_items(max_days=14, max_items=80)
    except Exception as e:
        logger.warning("recall API sync skipped: %s", e)
        return items

def _load_sanction_rows_sync(*, allow_api_fetch: bool = True) -> list[dict[str, str]]:
    from mfds_user.adapter.outbound.cache.food_safety_sanction_cache import (
        fetch_sanction_catalog_for_sync,
        get_cached_sanctions,
    )
    items, _, _, _, _ = get_cached_sanctions()
    if not allow_api_fetch:
        return items
    if len(items) >= 20:
        return items
    try:
        # 영업취소/시정명령은 최신 100건에 항상 포함되지 않을 수 있어
        # DB 캐시를 충분히 채우기 위해 더 넓게 적재한다. (catalog 파일 기반이라 외부 API 추가 호출 없음)
        return fetch_sanction_catalog_for_sync(max_items=1000)
    except Exception as e:
        logger.warning("sanction API sync skipped: %s", e)
        return items

async def sync_recalls_to_db(session: AsyncSession, *, allow_api_fetch: bool = True) -> int:
    rows = await asyncio.to_thread(_load_recall_rows_sync, allow_api_fetch=allow_api_fetch)
    return await sync_recall_dict_rows(session, rows)

async def sync_recall_dict_rows(session: AsyncSession, rows: list[dict[str, str]]) -> int:
    now = datetime.utcnow()
    inserted = 0
    updated = 0
    skipped = 0
    for row in rows:
        schema = _recall_row_to_schema(row)
        if schema is None:
            continue
        existing = await session.get(RecallModel, schema.id)
        new_fp = _raw_json_fingerprint(row)
        if existing is not None:
            old_fp = _raw_json_fingerprint(existing.raw_json if isinstance(existing.raw_json, dict) else {})
            if old_fp == new_fp:
                skipped += 1
                continue
            existing.product_name = schema.product_name
            existing.manufacturer = schema.manufacturer
            existing.food_type = schema.food_type
            existing.food_category = schema.food_category
            existing.recall_reason = schema.recall_reason
            existing.recall_grade = schema.recall_grade
            existing.recall_method = schema.recall_method
            existing.registered_at = schema.registered_at
            existing.image_url = schema.image_url
            existing.raw_json = dict(row)
            existing.fetched_at = now
            updated += 1
        else:
            model = RecallModel(
                id=schema.id,
                product_name=schema.product_name,
                manufacturer=schema.manufacturer,
                food_type=schema.food_type,
                food_category=schema.food_category,
                recall_reason=schema.recall_reason,
                recall_grade=schema.recall_grade,
                recall_method=schema.recall_method,
                registered_at=schema.registered_at,
                image_url=schema.image_url,
                raw_json=dict(row),
                fetched_at=now,
            )
            session.add(model)
            inserted += 1
    if inserted or updated:
        await session.commit()
    logger.info("recalls_cache upsert_many inserted=%s updated=%s skipped=%s", inserted, updated, skipped)
    return inserted + updated

async def enrich_recalls_from_api(session: AsyncSession, *, max_items: int = 100) -> int:
    from mfds_user.adapter.outbound.cache.food_safety_recall_cache import (
        fetch_recall_catalog_for_sync,
    )
    rows = await asyncio.to_thread(fetch_recall_catalog_for_sync, max_items=max_items)
    if not rows:
        return 0
    return await sync_recall_dict_rows(session, rows)

async def sync_enforcement_dict_rows(session: AsyncSession, rows: list[dict[str, str]]) -> int:
    now = datetime.utcnow()
    inserted = 0
    updated = 0
    skipped = 0
    seen_ids: set[str] = set()
    for row in rows:
        schema = _sanction_row_to_schema(row)
        if schema is None:
            continue
        # catalog/일자 수집 결과에서 동일 id가 중복될 수 있어 (서비스별 병합, window fetch 등)
        # 중복 insert로 스케줄러가 실패하지 않게 방지한다.
        if schema.id in seen_ids:
            skipped += 1
            continue
        seen_ids.add(schema.id)
        existing = await session.get(EnforcementModel, schema.id)
        new_fp = _raw_json_fingerprint(row)
        if existing is not None:
            old_fp = _raw_json_fingerprint(existing.raw_json if isinstance(existing.raw_json, dict) else {})
            if old_fp == new_fp:
                skipped += 1
                continue
            existing.business_name = schema.business_name
            existing.business_type = schema.business_type
            existing.address = schema.address
            existing.process_type = schema.process_type
            existing.violation_content = schema.violation_content
            existing.violation_date = schema.violation_date
            existing.process_date = schema.process_date
            existing.district = schema.district
            existing.raw_json = dict(row)
            existing.fetched_at = now
            updated += 1
        else:
            model = EnforcementModel(
                id=schema.id,
                business_name=schema.business_name,
                business_type=schema.business_type,
                address=schema.address,
                process_type=schema.process_type,
                violation_content=schema.violation_content,
                violation_date=schema.violation_date,
                process_date=schema.process_date,
                district=schema.district,
                raw_json=dict(row),
                fetched_at=now,
            )
            session.add(model)
            inserted += 1
    if inserted or updated:
        await session.commit()
    logger.info("enforcement_cache upsert_many inserted=%s updated=%s skipped=%s", inserted, updated, skipped)
    return inserted + updated

async def sync_enforcements_to_db(session: AsyncSession, *, allow_api_fetch: bool = True) -> int:
    rows = await asyncio.to_thread(_load_sanction_rows_sync, allow_api_fetch=allow_api_fetch)
    return await sync_enforcement_dict_rows(session, rows)

async def enrich_enforcements_from_api(session: AsyncSession, *, max_items: int = 100) -> int:
    from mfds_user.adapter.outbound.cache.api_result import is_api_quota_blocked
    from mfds_user.adapter.outbound.cache.food_safety_sanction_cache import (
        fetch_sanction_catalog_for_sync,
    )
    if is_api_quota_blocked():
        logger.warning("enforcement enrich skipped: OpenAPI daily quota exceeded (INFO-300)")
        return 0
    rows = await asyncio.to_thread(fetch_sanction_catalog_for_sync, max_items=max_items)
    if not rows:
        return 0
    return await sync_enforcement_dict_rows(session, rows)

async def ensure_food_safety_db_cache(session: AsyncSession, *, allow_api_fetch: bool = False) -> None:
    res_rec = await session.execute(select(func.count()).select_from(RecallModel))
    recall_n = int(res_rec.scalar_one())
    if recall_n == 0:
        await sync_recalls_to_db(session, allow_api_fetch=allow_api_fetch)

    res_enf = await session.execute(select(func.count()).select_from(EnforcementModel))
    enf_n = int(res_enf.scalar_one())
    if enf_n == 0:
        await sync_enforcements_to_db(session, allow_api_fetch=allow_api_fetch)
