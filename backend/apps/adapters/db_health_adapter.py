from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class DbHealthAdapter:
    """DB 연결·시간 확인."""

    @staticmethod
    async def neon_time_check(db: AsyncSession):
        try:
            result = await db.execute(text("SELECT NOW();"))
            return {"status": "success", "neon_time": result.scalar()}
        except Exception as exc:
            return {"status": "error", "message": str(exc)}
