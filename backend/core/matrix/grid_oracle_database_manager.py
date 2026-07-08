"""Neon(PostgreSQL) 비동기 연결 — SQLAlchemy 2.0 DeclarativeBase (하이브리드)."""

from __future__ import annotations

import asyncio
import os
import sys
from collections.abc import AsyncGenerator, AsyncIterator
from pathlib import Path
from typing import Optional

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

# `grid_oracle_database_manager.py` 기준: com.auditor/.env (Keymaker와 동일한 파일)
load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")


def _normalize_async_database_url(url: str) -> str:
    """Neon 등에서 흔한 sync URL을 async SQLAlchemy용으로 변환합니다."""
    if url.startswith("postgresql+psycopg://"):
        return url.replace("postgresql+psycopg://", "postgresql+psycopg_async://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg_async://", 1)
    return url


def normalize_sync_database_url(url: str) -> str:
    """Alembic 등 동기 마이그레이션용 URL (psycopg3 sync 드라이버)."""
    if url.startswith("postgresql+psycopg_async://"):
        return url.replace("postgresql+psycopg_async://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = (os.getenv("DATABASE_URL") or "").strip()
ASYNC_DATABASE_URL = _normalize_async_database_url(DATABASE_URL) if DATABASE_URL else ""
SYNC_DATABASE_URL = normalize_sync_database_url(DATABASE_URL) if DATABASE_URL else ""


class Base(DeclarativeBase):
    """공통 DeclarativeBase — Alembic autogenerate·Mapped ORM 단일 metadata.

    `mfds` 회원·관리자 테이블은 SQLModel(`SQLModel.metadata`)로 별도 관리됩니다.
    """


engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None
# FastAPI·기존 코드 호환 alias
AsyncSessionLocal: Optional[async_sessionmaker[AsyncSession]] = None


def init_engine() -> None:
    """DATABASE_URL이 있을 때만 비동기 엔진·세션 팩토리를 지연 초기화합니다."""
    global engine, async_session_factory, AsyncSessionLocal

    if not ASYNC_DATABASE_URL:
        return
    if engine is not None:
        return

    engine = create_async_engine(
        ASYNC_DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_recycle=280,
        connect_args={"connect_timeout": 10},
    )
    async_session_factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
        autoflush=False,
    )
    AsyncSessionLocal = async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    if async_session_factory is None:
        init_engine()
    if async_session_factory is None:
        raise HTTPException(
            status_code=503,
            detail="DATABASE_URL이 설정되지 않았습니다. com.auditor/.env 에 Neon 연결 문자열을 추가하세요.",
        )
    async with async_session_factory() as session:
        yield session


async def get_db_optional() -> AsyncIterator[AsyncSession | None]:
    """DB가 없을 때는 None을 넘깁니다(공개 가입 등)."""
    if not ASYNC_DATABASE_URL:
        yield None
        return
    if async_session_factory is None:
        init_engine()
    if async_session_factory is None:
        yield None
        return
    async with async_session_factory() as session:
        yield session


async def create_all_tables() -> None:
    """등록된 ORM 모델 기준으로 테이블을 생성합니다 (로컬·수업용 보조)."""
    if engine is None:
        init_engine()
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def dispose_engine() -> None:
    """앱 종료 시 비동기 엔진·세션 팩토리를 정리합니다."""
    global engine, async_session_factory, AsyncSessionLocal
    if engine is not None:
        await engine.dispose()
    engine = None
    async_session_factory = None
    AsyncSessionLocal = None


# lifespan·백그라운드·CLI가 import만으로 세션 팩토리를 쓰는 기존 코드 호환
if ASYNC_DATABASE_URL:
    init_engine()
