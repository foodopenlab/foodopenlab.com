from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from uuid import UUID
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_admin.app.ports.output.logs_repository import LogsRepositoryPort
from mfds_admin.app.dtos.logs_dto import ApiUsageLogDTO, SearchLogDTO
from mfds_admin.adapter.outbound.orm.api_usage_log_orm import ApiUsageLogORM
from mfds_admin.adapter.outbound.orm.search_log_orm import SearchLogORM
from mfds_user.adapter.outbound.orm.expert_user_orm import ExpertUserORM
from mfds_user.adapter.outbound.orm.agent_message_orm import AgentMessageORM

class LogsPgRepository(LogsRepositoryPort):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_api_logs(self, page: int, size: int, api_name: Optional[str] = None) -> Tuple[List[ApiUsageLogDTO], int]:
        # Count total
        count_stmt = select(func.count()).select_from(ApiUsageLogORM)
        if api_name:
            count_stmt = count_stmt.where(ApiUsageLogORM.api_name == api_name)
        count_res = await self.session.execute(count_stmt)
        total = int(count_res.scalar_one())

        # Fetch items
        stmt = select(ApiUsageLogORM)
        if api_name:
            stmt = stmt.where(ApiUsageLogORM.api_name == api_name)
        stmt = stmt.order_by(ApiUsageLogORM.called_at.desc()).offset((page - 1) * size).limit(size)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()

        items = [
            ApiUsageLogDTO(
                id=r.id,
                actor_type=r.actor_type,
                actor_id=r.actor_id,
                api_name=r.api_name,
                called_at=r.called_at,
                response_time_ms=r.response_time_ms,
                status_code=r.status_code,
                response_ms=r.response_time_ms,
                is_cache_hit=False,
                endpoint=None
            )
            for r in rows
        ]
        return items, total

    async def get_search_logs(self, page: int, size: int, query_pattern: Optional[str] = None) -> Tuple[List[SearchLogDTO], int]:
        # Count total
        count_stmt = select(func.count()).select_from(SearchLogORM)
        if query_pattern:
            count_stmt = count_stmt.where(SearchLogORM.query_pattern == query_pattern)
        count_res = await self.session.execute(count_stmt)
        total = int(count_res.scalar_one())

        # Fetch items
        stmt = select(SearchLogORM)
        if query_pattern:
            stmt = stmt.where(SearchLogORM.query_pattern == query_pattern)
        stmt = stmt.order_by(SearchLogORM.searched_at.desc()).offset((page - 1) * size).limit(size)
        res = await self.session.execute(stmt)
        rows = res.scalars().all()

        items = [
            SearchLogDTO(
                id=r.id,
                actor_type=r.actor_type,
                actor_id=r.actor_id,
                keyword=r.keyword,
                query_pattern=r.query_pattern,
                searched_at=r.searched_at
            )
            for r in rows
        ]
        return items, total

    async def get_api_stats_summary(self, start_date: datetime, end_date: datetime) -> dict:
        stmt = (
            select(
                ApiUsageLogORM.api_name,
                func.count().label("total_calls"),
                func.avg(ApiUsageLogORM.response_time_ms).label("avg_ms"),
                func.count()
                .filter(
                    and_(
                        ApiUsageLogORM.status_code.isnot(None),
                        ApiUsageLogORM.status_code >= 400,
                    )
                )
                .label("error_count"),
            )
            .where(ApiUsageLogORM.called_at >= start_date, ApiUsageLogORM.called_at <= end_date)
            .group_by(ApiUsageLogORM.api_name)
            .order_by(func.count().desc())
        )
        res = await self.session.execute(stmt)
        
        stats = []
        for api_name, total_calls, avg_ms, error_count in res.all():
            stats.append({
                "api_name": api_name,
                "total_calls": total_calls,
                "cache_hits": 0,
                "avg_response_ms": float(avg_ms) if avg_ms is not None else 0.0,
                "error_count": error_count
            })
        return {"stats": stats}

    async def count_chats_today(self) -> dict:
        now = datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        today_total_stmt = select(func.count(AgentMessageORM.id)).where(
            and_(
                AgentMessageORM.created_at >= day_start,
                AgentMessageORM.created_at < day_end
            )
        )
        today_total_res = await self.session.execute(today_total_stmt)
        today_total = int(today_total_res.scalar_one())

        analysis_stmt = select(func.count(func.distinct(AgentMessageORM.session_id))).where(
            AgentMessageORM.query_pattern.in_(["ingredient", "haccp", "general"])
        )
        analysis_res = await self.session.execute(analysis_stmt)
        analysis_total = int(analysis_res.scalar_one())

        regulation_stmt = select(func.count(func.distinct(AgentMessageORM.session_id))).where(
            AgentMessageORM.query_pattern == "law"
        )
        regulation_res = await self.session.execute(regulation_stmt)
        regulation_total = int(regulation_res.scalar_one())

        return {
            "today_total": today_total,
            "analysis_total": analysis_total,
            "regulation_total": regulation_total,
            "ingredient_total": analysis_total
        }

    async def count_users_summary(self) -> dict:
        total_stmt = select(func.count()).select_from(ExpertUserORM)
        total_res = await self.session.execute(total_stmt)
        total = int(total_res.scalar_one())

        active_stmt = select(func.count()).select_from(ExpertUserORM).where(ExpertUserORM.last_login.isnot(None))
        active_res = await self.session.execute(active_stmt)
        active = int(active_res.scalar_one())

        return {
            "total": total,
            "active": active,
        }

    async def get_api_dashboard_stats(self, start_date: datetime, end_date: datetime) -> dict:
        # today_calls
        calls_stmt = select(func.count()).select_from(ApiUsageLogORM).where(
            and_(
                ApiUsageLogORM.called_at >= start_date,
                ApiUsageLogORM.called_at <= end_date
            )
        )
        calls_res = await self.session.execute(calls_stmt)
        today_calls = int(calls_res.scalar_one())

        # today_errors
        errors_stmt = select(func.count()).select_from(ApiUsageLogORM).where(
            and_(
                ApiUsageLogORM.called_at >= start_date,
                ApiUsageLogORM.called_at <= end_date,
                ApiUsageLogORM.status_code >= 400
            )
        )
        errors_res = await self.session.execute(errors_stmt)
        today_errors = int(errors_res.scalar_one())

        # top_api
        top_stmt = (
            select(ApiUsageLogORM.api_name)
            .where(
                and_(
                    ApiUsageLogORM.called_at >= start_date,
                    ApiUsageLogORM.called_at <= end_date
                )
            )
            .group_by(ApiUsageLogORM.api_name)
            .order_by(func.count().desc())
            .limit(1)
        )
        top_res = await self.session.execute(top_stmt)
        top_api = top_res.scalar() or ""

        return {
            "today_calls": today_calls,
            "today_errors": today_errors,
            "top_api": top_api
        }

