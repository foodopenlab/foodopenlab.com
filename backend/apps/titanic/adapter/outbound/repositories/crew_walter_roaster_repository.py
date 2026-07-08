from __future__ import annotations

import asyncio
import logging

import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession

import matrix.grid_oracle_database_manager as _db_manager
from titanic.app.dtos.crew_walter_roaster_dto import WalterRoasterQuery, WalterRoasterResponse
from titanic.app.ports.output.crew_walter_roaster_port import WalterRoasterPort

logger = logging.getLogger(__name__)


def _to_sync_url(async_url: str) -> str:
    """asyncpg URL → psycopg2 URL 변환 (grid_oracle_database_manager 역방향)"""
    url = str(async_url)
    url = url.replace("postgresql+asyncpg://", "postgresql+psycopg2://")
    url = url.replace("postgresql+psycopg_async://", "postgresql+psycopg://")
    url = url.replace("postgres://", "postgresql+psycopg2://")
    return url


class WalterRoasterRepository(WalterRoasterPort):
    '''PostgreSQL을 이용한 월터의 승객 명단 관리 저장소'''

    _JOIN_SQL = """
        SELECT p.passenger_id, p.name, p.gender, p.age, p.sib_sp, p.parch, p.survived,
               b.pclass, b.ticket, b.fare, b.cabin, b.embarked
        FROM titanic_persons p
        LEFT JOIN titanic_bookings b ON b.passenger_id = p.passenger_id
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _sync_engine(self):
        _db_manager.init_engine()
        if _db_manager.SYNC_DATABASE_URL:
            return create_engine(_db_manager.SYNC_DATABASE_URL)
        if _db_manager.engine is None:
            raise RuntimeError("DATABASE_URL이 설정되지 않았습니다.")
        sync_url = _to_sync_url(_db_manager.engine.url.render_as_string(hide_password=False))
        return create_engine(sync_url)

    def _get_train_set_sync(self) -> pd.DataFrame:
        '''survived IS NOT NULL 인 승객 + 예약 정보를 데이터프레임으로 반환'''
        sql = self._JOIN_SQL + " WHERE p.survived IS NOT NULL"
        frame = pd.read_sql(sql, self._sync_engine())
        logger.info("[WalterRoasterRepository] get_train_set | rows=%s", len(frame))
        return frame

    def _get_test_set_sync(self) -> pd.DataFrame:
        '''survived IS NULL 인 승객 + 예약 정보를 데이터프레임으로 반환'''
        sql = self._JOIN_SQL + " WHERE p.survived IS NULL"
        frame = pd.read_sql(sql, self._sync_engine())
        logger.info("[WalterRoasterRepository] get_test_set | rows=%s", len(frame))
        return frame

    async def get_train_set(self) -> pd.DataFrame:
        return await asyncio.to_thread(self._get_train_set_sync)

    async def get_test_set(self) -> pd.DataFrame:
        return await asyncio.to_thread(self._get_test_set_sync)

    def _get_train_stats_sync(self) -> dict[str, int | float]:
        frame = self._get_train_set_sync()
        total = len(frame)
        if total == 0:
            return {"total": 0, "survived": 0, "deceased": 0, "survival_rate": 0.0}
        labels = pd.Series(pd.to_numeric(frame["survived"], errors="coerce")).fillna(0)
        survived = int(labels.astype(int).sum())
        deceased = total - survived
        return {
            "total": total,
            "survived": survived,
            "deceased": deceased,
            "survival_rate": round(survived / total * 100, 1),
        }

    async def get_train_stats(self) -> dict[str, int | float]:
        return await asyncio.to_thread(self._get_train_stats_sync)

    async def introduce_myself(self, query: WalterRoasterQuery) -> WalterRoasterResponse:
        '''월터의 자기 소개 레포지토리 구현 메소드'''

        logger.info(f"[WalterRoasterRepository] introduce_myself 진입 | request_data={query}")

        response: WalterRoasterResponse = WalterRoasterResponse(
            id=query.id * 10000,
            name=query.name + "가 레포지토리에 다녀옴"
        )
        return response
