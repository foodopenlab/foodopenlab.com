"""auth 테이블 생성 — main.py 스타트업에서 호출(다른 앱 db_init과 동일 패턴)."""

from __future__ import annotations

import logging

from matrix.grid_oracle_database_manager import Base, engine

# metadata 등록을 위해 ORM import (side-effect).
from auth.adapter.outbound.pg.auth_identity_orm import AuthIdentityORM

logger = logging.getLogger(__name__)


async def create_auth_tables() -> None:
    if engine is None:
        logger.warning("DATABASE_URL 미설정 — auth 테이블 생성을 건너뜁니다.")
        return
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all, tables=[AuthIdentityORM.__table__])
        logger.info("auth 테이블 초기화 완료 (auth_identities)")
    except Exception as exc:
        logger.error("auth 테이블 초기화 실패: %s", exc)
