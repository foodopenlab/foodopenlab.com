"""Admin 계정 시드 CLI — `com.auditor/`에서 실행.

Usage (from `com.auditor/`):
    python seed_admin.py
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# Add apps and core to sys.path
_BACKEND_DIR = Path(__file__).resolve().parent
_APPS_DIR = _BACKEND_DIR / "apps"
_CORE_DIR = _BACKEND_DIR / "core"
for _path in (_CORE_DIR, _APPS_DIR, _BACKEND_DIR):
    _path_str = str(_path)
    if _path.is_dir() and _path_str not in sys.path:
        sys.path.insert(0, _path_str)

from sqlalchemy import select
from matrix.grid_oracle_database_manager import AsyncSessionLocal, dispose_engine
from mfds_admin.adapter.outbound.orm.admin_orm import AdminORM
from mfds_user.app.services.security import hash_password

logger = logging.getLogger(__name__)

def _require_env(name: str) -> str:
    value = (os.getenv(name) or "").strip()
    if not value:
        raise SystemExit(f"{name} is not set. Add it to com.auditor/.env")
    return value

async def seed_admin() -> None:
    if AsyncSessionLocal is None:
        raise SystemExit("DATABASE_URL is not set. Add it to com.auditor/.env")

    email = _require_env("ADMIN_EMAIL")
    password = os.getenv("ADMIN_PASSWORD") or ""
    if not password:
        raise SystemExit("ADMIN_PASSWORD is not set. Add it to com.auditor/.env")
    name = (os.getenv("ADMIN_NAME") or "Admin").strip() or "Admin"

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AdminORM).where(AdminORM.email == email))
        admin = result.scalar_one_or_none()
        hashed = hash_password(password)

        if admin is None:
            session.add(
                AdminORM(
                    email=email,
                    hashed_password=hashed,
                    name=name
                )
            )
            await session.commit()
            print(f"Created admin: {email}")
            return

        admin.hashed_password = hashed
        admin.name = name
        await session.commit()
        print(f"Updated admin: {email}")

async def _main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        await seed_admin()
    finally:
        await dispose_engine()

def main() -> None:
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(_main())

if __name__ == "__main__":
    main()
