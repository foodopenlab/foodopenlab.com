"""MFDS startup background tasks (invoked from main lifespan)."""

from __future__ import annotations

import asyncio
import logging

from matrix.grid_oracle_database_manager import AsyncSessionLocal
from mfds_user.adapter.outbound.pg.food_safety_db_sync import (
    ensure_food_safety_db_cache,
    enrich_enforcements_from_api,
    enrich_recalls_from_api,
)
from mfds_user.adapter.outbound.haccp.haccp_sync_adapter import sync_haccp_certifications_to_db

logger = logging.getLogger(__name__)

def preload_food_safety_caches() -> None:
    """?붿뒪??罹먯떆瑜?硫붾え由ъ뿉 ?щ젮 泥??붿껌??利됱떆 ?묐떟?섎룄濡??⑸땲??"""
    from mfds_user.adapter.outbound.cache.food_safety_recall_cache import (
        get_cached_recalls,
    )
    from mfds_user.adapter.outbound.cache.food_safety_sanction_cache import (
        get_cached_sanctions,
    )

    get_cached_recalls()
    get_cached_sanctions()

async def run_scheduler_after_startup() -> None:
    from mfds_user.adapter.outbound.cache.recall_scheduler import (
        run_recall_daily_scheduler,
    )
    await run_recall_daily_scheduler()

async def background_enrich_recalls() -> None:
    if AsyncSessionLocal is None:
        return
    await asyncio.sleep(1.5)
    try:
        async with AsyncSessionLocal() as session:
            n = await enrich_recalls_from_api(session, max_items=100)
            if n:
                logger.info("background recall enrich: %s rows", n)
    except Exception as e:
        logger.warning("background recall enrich failed: %s", e)

async def background_enrich_haccp_certifications() -> None:
    if AsyncSessionLocal is None:
        return
    await asyncio.sleep(3.5)
    try:
        async with AsyncSessionLocal() as session:
            stats = await sync_haccp_certifications_to_db(session)
            if stats.touched:
                logger.info(
                    "background HACCP certification enrich: inserted=%s updated=%s skipped=%s",
                    stats.inserted,
                    stats.updated,
                    stats.skipped,
                )
    except Exception as e:
        logger.warning("background HACCP certification enrich failed: %s", e)

async def background_enrich_enforcements() -> None:
    from mfds_user.adapter.outbound.cache.food_safety_sanction_cache import is_enrich_running, set_enrich_running

    if AsyncSessionLocal is None:
        return
    await asyncio.sleep(2.5)
    if is_enrich_running():
        return
    set_enrich_running(True)
    try:
        async with AsyncSessionLocal() as session:
            n = await enrich_enforcements_from_api(session, max_items=100)
            if n:
                logger.info("background enforcement enrich: %s rows", n)
    except Exception as e:
        logger.warning("background enforcement enrich failed: %s", e)
    finally:
        set_enrich_running(False)

async def ensure_food_safety_db_cache_on_startup() -> None:
    if AsyncSessionLocal is None:
        return
    async with AsyncSessionLocal() as session:
        try:
            await ensure_food_safety_db_cache(session, allow_api_fetch=False)
        except Exception as e:
            logger.warning("food safety DB cache sync on startup failed: %s", e)

async def ensure_food_poisoning_stat_db_cache_on_startup() -> None:
    """식중독 통계 테이블이 비어 있으면(최초 배포) 다음 스케줄 슬롯까지 기다리지 않고 1회 즉시 동기화."""
    from mfds_user.adapter.outbound.pg.food_poisoning_stat_db_sync import (
        sync_food_poisoning_stats_to_db,
    )
    from mfds_user.adapter.outbound.pg.food_poisoning_stat_pg_repository import (
        FoodPoisoningStatPgRepository,
    )

    if AsyncSessionLocal is None:
        return
    async with AsyncSessionLocal() as session:
        try:
            count = await FoodPoisoningStatPgRepository(session=session).count_all()
            if count == 0:
                n = await sync_food_poisoning_stats_to_db(session)
                logger.info("food poisoning stat DB cache backfilled on startup: touched=%s", n)
        except Exception as e:
            logger.warning("food poisoning stat DB cache sync on startup failed: %s", e)
