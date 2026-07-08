"""Windows에서 psycopg async 호환을 위해 Selector 이벤트 루프를 먼저 설정한 뒤 uvicorn을 실행합니다."""
from __future__ import annotations

import asyncio
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["apps", "core"],
    )
