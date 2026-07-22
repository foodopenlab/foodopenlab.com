"""인증 전용 엔트리포인트 — auth.foodopenlab.com (별도 컨테이너).

발급(개인키)은 이 프로세스에만 존재한다. 비즈니스 백엔드(main.py)와 분리 배포하며,
같은 코드베이스·이미지를 쓰되 command만 `uvicorn auth_main:app`로 다르게 띄운다.

  uvicorn auth_main:app --host 0.0.0.0 --port 9000
"""

import asyncio
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# PYTHONPATH 없이도 apps·matrix 패키지를 찾도록 한다(main.py와 동일 규약).
_BACKEND_DIR = Path(__file__).resolve().parent
for _sub in ("core", "apps"):
    _p = _BACKEND_DIR / _sub
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from matrix.grid_oracle_database_manager import dispose_engine, init_engine  # noqa: E402
from auth.adapter.inbound.api import auth_router, wellknown_router  # noqa: E402
from auth.adapter.outbound.pg.db_init import create_auth_tables  # noqa: E402


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_engine()
    await create_auth_tables()
    yield
    await dispose_engine()


app = FastAPI(
    title="Foodopenlab Auth",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,  # 실서비스: 문서 비노출
)

# cross-origin 쿠키(httponly)를 쓰므로 credentials 허용 + origin은 반드시 명시(와일드카드 불가).
_DEFAULT_CORS_ORIGINS = [
    "https://foodopenlab.com",
    "https://www.foodopenlab.com",
    "http://localhost:3000",
]
_extra = [o.strip() for o in os.getenv("AUTH_CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEFAULT_CORS_ORIGINS + _extra,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(wellknown_router)


@app.get("/healthz")
async def healthz() -> dict:
    return {"ok": True}
