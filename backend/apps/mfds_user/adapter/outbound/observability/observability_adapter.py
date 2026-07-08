import logging
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Callable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.app.ports.output.observability_ports import SearchLoggerPort
from mfds_admin.adapter.outbound.orm.search_log_orm import SearchLogORM
from mfds_user.adapter.outbound.orm.anonymous_orm import AnonymousORM
from mfds_user.adapter.outbound.orm.expert_user_orm import ExpertUserORM

logger = logging.getLogger(__name__)

class SearchLoggerAdapter(SearchLoggerPort):
    def __init__(self, session_factory: Callable[[], AsyncSession]) -> None:
        self.session_factory = session_factory

    async def log_search(
        self,
        user_id: Optional[str],
        session_key: Optional[str],
        search_type: str,
        query_keyword: str,
    ) -> None:
        if not query_keyword or not query_keyword.strip():
            return

        async with self.session_factory() as session:
            try:
                actor_type = "anonymous"
                actor_id = None

                # 1. Try to resolve as expert user (UUID check)
                if user_id:
                    try:
                        actor_id = UUID(str(user_id))
                        # Verify if this expert user exists
                        user_exists = await session.execute(
                            select(ExpertUserORM.id).where(ExpertUserORM.id == actor_id)
                        )
                        if user_exists.scalar_one_or_none():
                            actor_type = "expert"
                        else:
                            # Not found in expert_users, reset actor_id to resolve via anonymous
                            actor_id = None
                    except ValueError:
                        # Not a valid UUID
                        actor_id = None

                # 2. If anonymous, resolve or create anonymous entry using session_key
                if actor_type == "anonymous" or actor_id is None:
                    actor_type = "anonymous"
                    cookie_id = session_key or "anonymous"
                    
                    stmt = select(AnonymousORM).where(AnonymousORM.cookie_id == cookie_id)
                    res = await session.execute(stmt)
                    anon = res.scalar_one_or_none()
                    if anon is None:
                        anon = AnonymousORM(
                            id=uuid4(),
                            cookie_id=cookie_id,
                            created_at=datetime.utcnow(),
                            last_seen=datetime.utcnow()
                        )
                        session.add(anon)
                        await session.commit()
                        await session.refresh(anon)
                    actor_id = anon.id

                # 3. Create and save SearchLogORM
                log_entry = SearchLogORM(
                    id=uuid4(),
                    actor_type=actor_type,
                    actor_id=actor_id,
                    keyword=query_keyword.strip(),
                    query_pattern=search_type,  # e.g. 'law' | 'ingredient' | 'haccp' | 'general'
                    searched_at=datetime.utcnow()
                )
                session.add(log_entry)
                await session.commit()
                logger.info("Search log saved successfully: %s", log_entry.id)
            except Exception as e:
                logger.warning("Failed to save search log: %s", e)
                await session.rollback()
