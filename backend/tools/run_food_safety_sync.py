"""식품안전나라 순차 동기화 수동 실행(개발·운영 예외).

Usage (repo root, .venv 활성화 권장):
  python com.auditor/tools/run_food_safety_sync.py

Usage (com.auditor/):
  python tools/run_food_safety_sync.py
"""
from __future__ import annotations

import asyncio
import sys
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from pathlib import Path

_BACKEND = Path(__file__).resolve().parents[1]
for p in (_BACKEND / "core", _BACKEND / "apps"):
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))


async def main() -> None:
    import os
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        stream=sys.stdout
    )
    os.environ["FOOD_SAFETY_SYNC_STAGGER_SEC"] = "1"

    from matrix.grid_keymaker_secret_manager import get_keymaker

    get_keymaker().load_env()
    from mfds_user.adapter.outbound.cache.recall_scheduler import (
        run_staggered_sync_wave,
    )
    from mfds_user.adapter.outbound.cache.api_result import clear_api_quota_block
    from datetime import datetime
    from zoneinfo import ZoneInfo

    clear_api_quota_block()
    slot = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%H:%M")
    print(f"Starting manual staggered sync (slot={slot})...")
    await run_staggered_sync_wave(wave="manual", slot_display=slot, clear_quota_block=True)
    print("Done.")


if __name__ == "__main__":
    asyncio.run(main())
