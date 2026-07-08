import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pathlib import Path
from sqlalchemy import select, func

_BACKEND = Path(__file__).resolve().parents[1]
for p in (_BACKEND / "core", _BACKEND / "apps"):
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

async def main():
    from matrix.grid_keymaker_secret_manager import get_keymaker
    get_keymaker().load_env()

    from matrix.grid_oracle_database_manager import async_session_factory
    if not async_session_factory:
        print("Async database factory is not initialized. No DATABASE_URL?")
        return

    from mfds_user.adapter.outbound.orm import (
        RecallModel,
        EnforcementModel,
        HaccpCertificationModel,
        SupplierModel
    )

    async with async_session_factory() as session:
        for model in [RecallModel, EnforcementModel, HaccpCertificationModel, SupplierModel]:
            try:
                stmt = select(func.count()).select_from(model)
                res = await session.execute(stmt)
                count = res.scalar()
                print(f"{model.__name__}: {count} records")
            except Exception as e:
                print(f"Error reading {model.__name__}: {e}")

if __name__ == "__main__":
    asyncio.run(main())

