"""식중독 통계(I2850/I2849) raw row → PostgreSQL food_poisoning_stat_cache 동기화."""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.adapter.outbound.cache.food_poisoning_stat_sync import (
    fetch_food_poisoning_stat_rows,
)
from mfds_user.adapter.outbound.orm.food_poisoning_stat_orm import FoodPoisoningStatModel

logger = logging.getLogger(__name__)


def _fingerprint(row: dict) -> str:
    return json.dumps(row, sort_keys=True, ensure_ascii=False, default=str)


def _row_id(row: dict[str, str]) -> str:
    raw = f"{row['category']}-{row['occurrence_year']}-{row['occurrence_month']}-{row['label']}"
    return raw[:64]


async def sync_food_poisoning_stat_rows(session: AsyncSession, rows: list[dict[str, str]]) -> int:
    now = datetime.utcnow()
    inserted = 0
    updated = 0
    skipped = 0
    for row in rows:
        rid = _row_id(row)
        existing = await session.get(FoodPoisoningStatModel, rid)
        new_fp = _fingerprint(row)
        if existing is not None:
            old_fp = _fingerprint(existing.raw_json if isinstance(existing.raw_json, dict) else {})
            if old_fp == new_fp:
                skipped += 1
                continue
            existing.incident_count = int(row.get("incident_count") or 0)
            existing.patient_count = int(row.get("patient_count") or 0)
            existing.raw_json = dict(row)
            existing.fetched_at = now
            updated += 1
        else:
            model = FoodPoisoningStatModel(
                id=rid,
                category=row["category"],
                label=row["label"],
                occurrence_year=row["occurrence_year"],
                occurrence_month=row.get("occurrence_month") or None,
                incident_count=int(row.get("incident_count") or 0),
                patient_count=int(row.get("patient_count") or 0),
                raw_json=dict(row),
                fetched_at=now,
            )
            session.add(model)
            inserted += 1
    if inserted or updated:
        await session.commit()
    logger.info(
        "food_poisoning_stat_cache upsert_many inserted=%s updated=%s skipped=%s", inserted, updated, skipped
    )
    return inserted + updated


async def sync_food_poisoning_stats_to_db(session: AsyncSession) -> int:
    rows = await asyncio.to_thread(fetch_food_poisoning_stat_rows)
    if not rows:
        return 0
    return await sync_food_poisoning_stat_rows(session, rows)
