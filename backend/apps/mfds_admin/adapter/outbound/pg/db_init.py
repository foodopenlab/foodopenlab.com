import logging
from matrix.grid_oracle_database_manager import Base, engine
# Import all ORM models to register them in metadata
from mfds_admin.adapter.outbound.orm import *

logger = logging.getLogger(__name__)

async def create_admin_tables() -> None:
    if engine is None:
        logger.warning("DATABASE_URL not set - skipping Admin table creation")
        return
    try:
        async with engine.begin() as conn:
            # Create admin ORM models
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Admin tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Admin tables: {e}")
