import logging

from matrix.grid_oracle_database_manager import Base, engine

# ORM 모델을 metadata에 등록하기 위해 import
from ontology.adapter.outbound.orm import *  # noqa: F401,F403

logger = logging.getLogger(__name__)


async def create_ontology_tables() -> None:
    if engine is None:
        logger.warning("DATABASE_URL not set - skipping Ontology table creation")
        return
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Ontology tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Ontology tables: {e}")
