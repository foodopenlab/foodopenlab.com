"""타이타닉 테이블 존재 확인 — 스키마 생성은 Alembic(`alembic upgrade head`) 전담."""

from __future__ import annotations

import asyncio
import logging

from sqlalchemy import inspect, text

from matrix.grid_oracle_database_manager import engine, init_engine
from titanic.adapter.outbound.orm import passenger_jack_trainer_orm, titanic_booking_orm  # noqa: F401 — metadata 등록
from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.adapter.outbound.orm.titanic_booking_orm import TitanicBookingOrm

logger = logging.getLogger(__name__)

_LEGACY_TABLES = ("titanic_passengers", "titanic_records")
_EXPECTED_TABLES = (
    JackTrainerOrm.__tablename__,
    TitanicBookingOrm.__tablename__,
)


async def create_titanic_tables() -> None:
    """``titanic_persons`` · ``titanic_bookings`` 존재 여부만 확인합니다."""
    init_engine()
    if engine is None:
        logger.warning("DATABASE_URL 미설정 — titanic 테이블 확인을 건너뜁니다.")
        return

    def _check_sync(sync_conn) -> tuple[list[str], list[str]]:
        insp = inspect(sync_conn)
        for legacy in _LEGACY_TABLES:
            if insp.has_table(legacy):
                logger.warning("legacy 테이블 '%s' 제거 (alembic과 별도)", legacy)
                sync_conn.execute(text(f'DROP TABLE IF EXISTS "{legacy}" CASCADE'))
        missing = [t for t in _EXPECTED_TABLES if not insp.has_table(t)]
        present = [t for t in _EXPECTED_TABLES if t not in missing]
        return missing, present

    try:
        async with asyncio.timeout(30):
            async with engine.begin() as conn:
                missing, present = await conn.run_sync(_check_sync)
        if missing:
            logger.warning(
                "titanic 테이블 없음: %s — Neon 스키마는 `cd com.auditor && alembic upgrade head` 로 생성하세요.",
                missing,
            )
        else:
            logger.info("titanic tables ready: %s", present)
    except Exception as exc:
        logger.warning("titanic 테이블 확인 실패(앱은 계속 실행): %s", exc)
