import logging
from sqlmodel import SQLModel
from sqlalchemy import text
from matrix.grid_oracle_database_manager import Base, engine
# Import all ORM models to register them in metadata
from mfds_user.adapter.outbound.orm import *

logger = logging.getLogger(__name__)

async def create_user_tables() -> None:
    if engine is None:
        logger.warning("DATABASE_URL not set - skipping User table creation")
        return
    try:
        async with engine.begin() as conn:
            # Create user ORM models
            await conn.run_sync(Base.metadata.create_all)
            await conn.run_sync(SQLModel.metadata.create_all)
            
            # Drop foreign key constraints on message_id to support polymorphic referencing
            await conn.execute(text("ALTER TABLE satisfaction_feedbacks DROP CONSTRAINT IF EXISTS satisfaction_feedbacks_message_id_fkey"))
            await conn.execute(text("ALTER TABLE expert_feedbacks DROP CONSTRAINT IF EXISTS expert_feedbacks_message_id_fkey"))
        logger.info("User tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize User tables: {e}")
