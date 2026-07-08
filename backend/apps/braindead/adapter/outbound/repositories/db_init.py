from __future__ import annotations

import logging

from sqlalchemy import text

from matrix.grid_oracle_database_manager import Base, engine, init_engine
from braindead.adapter.outbound.orm import contact_orm as _  # noqa: F401
from braindead.adapter.outbound.orm import inbox_orm as ___  # noqa: F401
from braindead.adapter.outbound.orm import spam_orm as __  # noqa: F401

logger = logging.getLogger(__name__)


async def create_contact_tables() -> None:
    init_engine()
    if engine is None:
        logger.warning("DATABASE_URL 미설정 — braindead 테이블 생성을 건너뜁니다.")
        return
    try:
        async with engine.begin() as conn:
            # braindead_inbox.embedding(Vector) 컬럼용 — 테이블 생성 전에 확장 활성화 필요
            await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
            # create_all은 기존 테이블에 새 컬럼을 추가하지 않으므로 별도 보강
            await conn.execute(
                text("ALTER TABLE braindead_inbox ADD COLUMN IF NOT EXISTS embedding vector(1024)")
            )
        logger.info("braindead_contacts table ready")
    except Exception as exc:
        logger.warning("braindead 테이블 생성 실패(앱은 계속 실행): %s", exc)
