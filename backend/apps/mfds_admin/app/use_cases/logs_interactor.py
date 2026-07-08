from typing import List, Tuple, Optional
from datetime import datetime, timedelta
from mfds_admin.app.ports.input.logs_use_case import LogsUseCase
from mfds_admin.app.ports.output.logs_repository import LogsRepositoryPort
from mfds_admin.app.dtos.logs_dto import ApiUsageLogDTO, SearchLogDTO

class LogsInteractor(LogsUseCase):
    def __init__(self, repo: LogsRepositoryPort) -> None:
        self.repo = repo

    async def list_api_logs(self, page: int, size: int, api_name: Optional[str] = None) -> Tuple[List[ApiUsageLogDTO], int]:
        return await self.repo.get_api_logs(page, size, api_name)

    async def list_search_logs(self, page: int, size: int, query_pattern: Optional[str] = None) -> Tuple[List[SearchLogDTO], int]:
        return await self.repo.get_search_logs(page, size, query_pattern)

    async def get_dashboard_stats(self) -> dict:
        users = await self.repo.count_users_summary()
        chats = await self.repo.count_chats_today()
        
        now = datetime.utcnow()
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        api = await self.repo.get_api_dashboard_stats(day_start, now)
        return {
            "users": users,
            "chats": chats,
            "api": api
        }

    def _period_bounds(self, period: str) -> tuple[datetime, datetime]:
        now = datetime.utcnow()
        if period == "week":
            return now - timedelta(days=7), now
        if period == "month":
            return now - timedelta(days=30), now
        day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return day_start, now

    async def get_api_stats(self, period: str = "today") -> dict:
        if period not in ("today", "week", "month"):
            period = "today"
        start_date, end_date = self._period_bounds(period)
        res_summary = await self.repo.get_api_stats_summary(start_date, end_date)
        
        stats = []
        for s in res_summary["stats"]:
            total_calls = s["total_calls"]
            cache_hits = s["cache_hits"]
            error_count = s["error_count"]
            cache_hit_rate = (cache_hits / total_calls * 100.0) if total_calls else 0.0
            err_rate = (error_count / total_calls * 100.0) if total_calls else 0.0
            stats.append({
                "api_name": s["api_name"],
                "total_calls": total_calls,
                "cache_hits": cache_hits,
                "cache_hit_rate": round(cache_hit_rate, 2),
                "avg_response_ms": round(s["avg_response_ms"], 2),
                "error_count": error_count,
                "error_rate": round(err_rate, 2)
            })
        return {"period": period, "stats": stats}

