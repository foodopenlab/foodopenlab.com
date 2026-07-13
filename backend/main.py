import asyncio
import os
import sys

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import json
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

# psycopg async(=SQLAlchemy async)가 Windows에서 ProactorEventLoop를 만나면 실패합니다.
# 이벤트 루프 정책이 실제로 Selector로 잡히는지 로그로 남겨 문제 재현을 빠르게 합니다.
try:
    logging.getLogger("titanic.upload").info(
        "asyncio event loop policy=%s",
        type(asyncio.get_event_loop_policy()).__name__,
    )
except Exception:
    pass

# uvicorn 실행 시 PYTHONPATH=apps 없이도 apps·matrix 패키지를 찾도록 한다.
_BACKEND_DIR = Path(__file__).resolve().parent
_CORE_DIR = _BACKEND_DIR / "core"
_APPS_DIR = _BACKEND_DIR / "apps"
for _path in (_CORE_DIR, _APPS_DIR):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

try:
    from matrix.grid_keymaker_secret_manager import get_keymaker

    keymaker = get_keymaker()
    keymaker.load_env()

    from matrix.external_api_budget import (
        ExternalApiBudgetExceeded,  # type: ignore[assignment]
        get_external_api_usage_state,
    )
except ModuleNotFoundError:
    class _KeymakerStub:
        def load_env(self) -> None: ...

        def is_gemini_ready(self) -> bool:
            return False

        def generate_content(self, _message: str) -> str:
            raise RuntimeError("matrix.grid_keymaker_secret_manager is not available")

        def is_quota_error(self, _e: Exception) -> bool:
            return False

        def get_gemini_model_name(self) -> str:
            return "unavailable"

        def get_secret(self, _key: str) -> str | None:
            return None

    keymaker = _KeymakerStub()

    class ExternalApiBudgetExceeded(Exception):
        def __init__(self, message: str = "External API budget exceeded") -> None:
            super().__init__(message)
            self.message = message

    def get_external_api_usage_state() -> dict[str, Any]:
        return {"available": False, "reason": "matrix app missing"}

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from adapters.db_health_adapter import DbHealthAdapter
from matrix.grid_oracle_database_manager import dispose_engine, get_db, init_engine
from mfds_user.adapter.inbound.api import user_router
from mfds_admin.adapter.inbound.api import admin_router
from mfds_user.adapter.outbound.cache.lifecycle import (
    ensure_food_poisoning_stat_db_cache_on_startup,
    ensure_food_safety_db_cache_on_startup,
    preload_food_safety_caches,
    run_scheduler_after_startup,
)
from mfds_user.adapter.outbound.pg.db_init import create_user_tables
from mfds_admin.adapter.outbound.pg.db_init import create_admin_tables
from titanic.adapter.inbound.api import titanic_router
from titanic.adapter.outbound.repositories.db_init import create_titanic_tables
from siliconvalley.adapter.inbound.api import piper_router
from braindead.adapter.inbound.api import braindead_router
from braindead.adapter.outbound.repositories.db_init import create_contact_tables
from ontology.adapter.inbound.api import vision_router


logger = logging.getLogger(__name__)


def _configure_app_logging() -> None:
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    if log.handlers:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(levelname)s:%(name)s:%(message)s"))
    log.addHandler(handler)
    log.propagate = False


_configure_app_logging()


def _ensure_titanic_logging() -> None:
    """titanic 업로드/조회 흐름 로그를 uvicorn 터미널에 출력합니다."""
    fmt = logging.Formatter("%(levelname)s:%(name)s:%(message)s")
    for name in ("titanic", "titanic.upload"):
        log = logging.getLogger(name)
        log.setLevel(logging.INFO)
        log.disabled = False
        for h in list(log.handlers):
            log.removeHandler(h)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(fmt)
        handler.setLevel(logging.INFO)
        log.addHandler(handler)
        log.propagate = False


_ensure_titanic_logging()
logging.getLogger("titanic.upload").info("titanic trace logging enabled (upload + reader)")


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


class SeoulWeatherResponse(BaseModel):
    city: str
    temp_c: int
    description: str
    icon: str


def _gemini_chat_reply(message: str) -> str:
    if not keymaker.is_gemini_ready():
        raise HTTPException(
            status_code=503,
            detail="GEMINI_API_KEY가 설정되지 않았습니다. com.auditor/.env 에 키를 넣어 주세요.",
        )

    try:
        response: Any = keymaker.generate_content(message)
    except ExternalApiBudgetExceeded as e:
        raise HTTPException(status_code=429, detail=e.message) from e
    except Exception as e:
        err = str(e)
        if keymaker.is_quota_error(e):
            raise HTTPException(
                status_code=429,
                detail=(
                    "Gemini API 무료 할당량을 초과했습니다. "
                    "잠시 후 다시 시도하거나, Google AI Studio에서 사용량·요금제를 확인해 주세요. "
                    f"(모델: {keymaker.get_gemini_model_name()}) "
                    "com.auditor/.env 의 GEMINI_MODEL 을 gemini-3.5-flash 등으로 바꿔 볼 수 있습니다."
                ),
            ) from e
        raise HTTPException(
            status_code=502,
            detail=f"Gemini 호출 실패: {err}",
        ) from e

    try:
        text = (response.text or "").strip()
    except ValueError as e:
        feedback = getattr(response, "prompt_feedback", None)
        raise HTTPException(
            status_code=400,
            detail=f"응답 텍스트를 읽을 수 없습니다: {e!s}. prompt_feedback={feedback}",
        ) from e

    if not text:
        reason = None
        if getattr(response, "candidates", None):
            c0 = response.candidates[0]
            reason = getattr(c0, "finish_reason", None)
        raise HTTPException(
            status_code=502,
            detail=(
                "모델이 비어 있는 응답을 반환했습니다."
                + (f" (finish_reason={reason})" if reason else "")
            ),
        )

    return text


from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def crawl_and_collect():
    logger.info("Scheduled data collection job triggered (Step 1). All live adapters are ready for Step 2.")

async def generate_daily_reports():
    logger.info("Scheduled daily briefing generation job triggered (Step 2)...")
    from matrix.grid_oracle_database_manager import async_session_factory

    if async_session_factory is None:
        logger.error("async_session_factory is None - skipping scheduled report generation")
        return

    async with async_session_factory() as session:
        try:
            from mfds_user.dependencies.daily_report import build_report_scheduler_use_case
            use_case = build_report_scheduler_use_case(session)
            res = await use_case.generate_all()
            logger.info(f"Scheduled daily briefing generation finished successfully: {res}")
        except Exception as e:
            logger.error(f"Scheduled daily briefing generation failed: {e}", exc_info=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_titanic_logging()
    init_engine()
    await create_user_tables()
    await create_admin_tables()
    await create_titanic_tables()
    await create_contact_tables()
    await asyncio.to_thread(preload_food_safety_caches)
    await ensure_food_safety_db_cache_on_startup()
    await ensure_food_poisoning_stat_db_cache_on_startup()

    # Register daily report scheduler
    scheduler = AsyncIOScheduler(timezone="Asia/Seoul")
    scheduler.add_job(
        crawl_and_collect,
        "cron",
        hour=9,
        minute=40,
    )
    scheduler.add_job(
        generate_daily_reports,
        "cron",
        hour=10,
        minute=30,
    )
    scheduler.start()
    logger.info("Daily report scheduler started (Step 1: 09:40, Step 2: 10:30)")

    scheduler_task: asyncio.Task[None] | None = None
    if os.getenv("DISABLE_FOOD_SAFETY_SCHEDULER", "").strip().lower() not in {
        "1",
        "true",
        "yes",
    }:
        scheduler_task = asyncio.create_task(run_scheduler_after_startup())
    else:
        logger.info("food safety scheduler disabled (DISABLE_FOOD_SAFETY_SCHEDULER)")
    try:
        yield
    finally:
        scheduler.shutdown()
        logger.info("Daily report scheduler stopped")
        if scheduler_task is not None:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                pass
        await dispose_engine()


app = FastAPI(title="Foodopenlab Main Page", lifespan=lifespan)

# 로컬 개발용 기본 오리진. 운영 도메인(Vercel/Cloudflare)은 CORS_ORIGINS 환경변수로 추가한다.
# 예) CORS_ORIGINS=https://foodopenlab.com,https://www.foodopenlab.com
_DEFAULT_CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.0.49:3000",
]
_extra_cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "").split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_DEFAULT_CORS_ORIGINS + _extra_cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(admin_router)
app.include_router(titanic_router, prefix="/api")
app.include_router(piper_router, prefix="/api")
app.include_router(braindead_router, prefix="/api")
app.include_router(vision_router, prefix="/api")


@app.exception_handler(ExternalApiBudgetExceeded)
async def _external_api_budget_handler(_request: Request, exc: ExternalApiBudgetExceeded) -> JSONResponse:
    return JSONResponse(status_code=429, content={"detail": exc.message})


@app.exception_handler(HTTPException)
async def _http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    detail = exc.detail
    if isinstance(detail, list):
        detail = jsonable_encoder(detail)
    return JSONResponse(status_code=exc.status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("unhandled error path=%s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "서버 내부 오류가 발생했습니다. 잠시 후 다시 시도해 주세요."})


@app.get("/")
def read_root():
    print("루트 경로 실행 중")
    return {"message": "FAST API 메인 페이지 ", "docs": "/docs"}


@app.get("/health")
async def health_check():
    """프론트·프록시 연동 확인용 헬스 체크 (이벤트 루프에서 즉시 응답)."""
    body: dict[str, Any] = {"status": "ok"}
    st = get_external_api_usage_state()
    if st.get("daily_limit", 0):
        body["external_api_budget"] = st
    return body


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    """JSON 본문 `{"message": "..."}` 를 받아 Gemini 답변 문자열을 반환합니다."""
    return ChatResponse(reply=_gemini_chat_reply(req.message))


@app.get("/weather/seoul", response_model=SeoulWeatherResponse)
async def get_seoul_weather() -> SeoulWeatherResponse:
    """OpenWeatherMap — 서울 현재 날씨 (키: com.auditor/.env `WEATHER_API_KEY`)."""
    return await asyncio.to_thread(_fetch_seoul_weather_sync)


def _fetch_seoul_weather_sync() -> SeoulWeatherResponse:
    api_key = keymaker.get_secret("WEATHER_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="WEATHER_API_KEY가 설정되지 않았습니다. com.auditor/.env 에 키를 넣어 주세요.",
        )

    query = urlencode({"q": "Seoul,KR", "appid": api_key, "units": "metric", "lang": "kr"})
    url = f"https://api.openweathermap.org/data/2.5/weather?{query}"

    from matrix.external_api_budget import consume_external_api_unit_or_raise

    consume_external_api_unit_or_raise(units=1, label="weather.openweathermap")

    try:
        with urlopen(url, timeout=10) as resp:
            payload = json.loads(resp.read().decode())
    except HTTPError as e:
        raise HTTPException(status_code=502, detail=f"날씨 API 오류: {e.code}") from e
    except URLError as e:
        raise HTTPException(status_code=502, detail=f"날씨 API 연결 실패: {e.reason}") from e
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"날씨 API 호출 실패: {e!s}") from e

    weather = (payload.get("weather") or [{}])[0]
    main = payload.get("main") or {}
    return SeoulWeatherResponse(
        city="서울",
        temp_c=round(float(main.get("temp", 0))),
        description=str(weather.get("description", "")),
        icon=str(weather.get("icon", "01d")),
    )


@app.get("/db-check")
async def check_db(db: AsyncSession = Depends(get_db)):
    return await DbHealthAdapter.neon_time_check(db)


if __name__ == "__main__":
    import uvicorn
    print("메인 파일 실행##########################################")

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
