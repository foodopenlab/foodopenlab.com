"""매일 09:40·17:40(KST) 식품안전나라 OpenAPI 서비스 간격 호출 → catalog/DB 동기화."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from mfds_user.adapter.outbound.cache.api_result import (
    clear_api_quota_block_for_new_day,
    is_api_quota_blocked,
)
from mfds_user.adapter.outbound.cache.mfds_silence import (
    is_mfds_silenced,
    silenced_until,
)
from mfds_user.adapter.outbound.cache.food_safety_recall_cache import (
    sync_recall_catalog_from_api,
)
from mfds_user.adapter.outbound.cache.food_safety_sanction_cache import (
    SANCTION_SERVICES,
    finalize_sanction_latest_from_catalog,
    set_active_sync_context,
    sync_sanction_service_to_catalog,
)
from mfds_user.adapter.outbound.cache.food_safety_sync_slots import (
    next_sync_slot_kst,
    stagger_seconds,
)
from mfds_user.adapter.outbound.cache.food_safety_sync_state import (
    record_sync_wave_completed,
)

logger = logging.getLogger(__name__)

_manual_sync_lock = asyncio.Lock()
_manual_sync_running = False
_stagger_sec_override: int | None = None
KST = ZoneInfo("Asia/Seoul")

async def _sleep_stagger() -> None:
    sec = _stagger_sec_override if _stagger_sec_override is not None else stagger_seconds()
    await asyncio.sleep(sec)

async def _sync_food_safety_to_db() -> None:
    from matrix.grid_oracle_database_manager import AsyncSessionLocal
    from mfds_user.adapter.outbound.pg.food_safety_db_sync import (
        enrich_enforcements_from_api,
        enrich_recalls_from_api,
    )

    if AsyncSessionLocal is None or is_api_quota_blocked():
        return
    async with AsyncSessionLocal() as session:
        n_recall = await enrich_recalls_from_api(session, max_items=100)
        n_enf = await enrich_enforcements_from_api(session, max_items=100)
        logger.info("food safety DB sync from stored catalogs: recalls=%s enforcement=%s", n_recall, n_enf)

async def _sync_food_poisoning_stats_to_db() -> None:
    from matrix.grid_oracle_database_manager import AsyncSessionLocal
    from mfds_user.adapter.outbound.pg.food_poisoning_stat_db_sync import (
        sync_food_poisoning_stats_to_db,
    )

    if AsyncSessionLocal is None or is_api_quota_blocked():
        return
    async with AsyncSessionLocal() as session:
        n = await sync_food_poisoning_stats_to_db(session)
        logger.info("food poisoning stat DB sync: touched=%s", n)

async def _sync_haccp_to_db() -> None:
    from matrix.grid_oracle_database_manager import AsyncSessionLocal
    from mfds_user.adapter.outbound.haccp.haccp_sync_adapter import sync_haccp_certifications_to_db

    if AsyncSessionLocal is None or is_api_quota_blocked():
        return
    async with AsyncSessionLocal() as session:
        n = await sync_haccp_certifications_to_db(session)
        logger.info(
            "HACCP certification DB sync: inserted=%s updated=%s skipped=%s",
            n.inserted,
            n.updated,
            n.skipped,
        )

async def run_staggered_sync_wave(
    *,
    wave: str,
    slot_display: str,
    clear_quota_block: bool = False,
) -> None:
    """?뚯닔 ???됱젙泥섎텇 3醫?媛꾧꺽) ??DB ??HACCP ?쒖감 ?숆린??"""
    global _stagger_sec_override
    if is_mfds_silenced():
        logger.warning(
            "food safety staggered sync SKIPPED (silenced until %s) wave=%s slot=%s",
            silenced_until(), wave, slot_display,
        )
        return
    if clear_quota_block:
        from mfds_user.adapter.outbound.cache.api_result import clear_api_quota_block
        clear_api_quota_block()
    clear_api_quota_block_for_new_day()
    set_active_sync_context(wave=wave, slot_display=slot_display)
    logger.info("food safety staggered sync start wave=%s slot=%s", wave, slot_display)

    recall_stats = await asyncio.to_thread(
        sync_recall_catalog_from_api,
        wave=wave,
        slot_display=slot_display,
    )
    logger.info(
        "recall catalog wave=%s added=%s updated=%s skipped=%s",
        wave,
        recall_stats.added,
        recall_stats.updated,
        recall_stats.skipped,
    )
    await _sleep_stagger()

    for service_id, category in SANCTION_SERVICES:
        stats = await asyncio.to_thread(sync_sanction_service_to_catalog, service_id, category)
        logger.info(
            "sanction %s wave=%s added=%s updated=%s skipped=%s",
            service_id,
            wave,
            stats.added,
            stats.updated,
            stats.skipped,
        )
        await _sleep_stagger()

    await asyncio.to_thread(finalize_sanction_latest_from_catalog)
    await _sync_food_safety_to_db()
    await _sleep_stagger()
    await _sync_food_poisoning_stats_to_db()
    await _sleep_stagger()
    await _sync_haccp_to_db()

    record_sync_wave_completed(wave=wave, slot_display=slot_display)
    logger.info("food safety staggered sync done wave=%s slot=%s", wave, slot_display)

async def run_food_safety_daily_scheduler() -> None:
    while True:
        target, wave, slot_display = next_sync_slot_kst()
        delay = max(1.0, (target - datetime.now(KST)).total_seconds())
        logger.info("next food safety sync at %s wave=%s (in %.0fs)", target.isoformat(), wave, delay)
        await asyncio.sleep(delay)
        try:
            await run_staggered_sync_wave(wave=wave, slot_display=slot_display)
        except Exception:
            logger.exception("food safety staggered sync failed wave=%s", wave)
        await asyncio.sleep(60)

async def trigger_manual_staggered_sync(*, force_quota: bool = True) -> dict:
    global _manual_sync_running, _stagger_sec_override
    if is_mfds_silenced():
        until = silenced_until()
        return {
            "started": False,
            "reason": "silenced",
            "silenced_until": until.isoformat() if until else None,
            "message": "식약처 외부 호출이 침묵(정지) 상태입니다. 해제 후 다시 시도하세요.",
        }
    async with _manual_sync_lock:
        if _manual_sync_running:
            return {"started": False, "reason": "already_running"}
        _manual_sync_running = True

    slot_display = datetime.now(KST).strftime("%H:%M")
    _stagger_sec_override = stagger_seconds(manual=True)

    async def _run() -> None:
        global _manual_sync_running, _stagger_sec_override
        try:
            await run_staggered_sync_wave(
                wave="manual",
                slot_display=slot_display,
                clear_quota_block=force_quota,
            )
        except Exception:
            logger.exception("manual food safety sync failed")
        finally:
            _stagger_sec_override = None
            async with _manual_sync_lock:
                _manual_sync_running = False

    asyncio.create_task(_run())
    return {
        "started": True,
        "wave": "manual",
        "slot_display": slot_display,
        "stagger_seconds": _stagger_sec_override,
        "message": "諛깃렇?쇱슫???쒖감 ?숆린?붽? ?쒖옉?섏뿀?듬땲?? ?쒕쾭 濡쒓렇?먯꽌 吏꾪뻾???뺤씤?섏꽭??",
    }

def is_manual_sync_running() -> bool:
    return _manual_sync_running

# ?섏쐞 ?명솚 留ㅽ븨
run_recall_daily_scheduler = run_food_safety_daily_scheduler
