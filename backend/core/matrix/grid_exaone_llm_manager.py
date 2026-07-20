"""로컬 Ollama(EXAONE) 추론 — apps/ 전역 공유 인프라.

추론 모델 **단일 소스(SSOT)**. 모든 앱은 이 매니저를 경유해 EXAONE를 호출하며,
모델 문자열을 앱마다 하드코딩하지 않으므로 추론 모델이 섞이지 않는다.
(임베딩 전용 `grid_embedding_manager`(bge-m3)와 대칭 구조.)
"""

from __future__ import annotations

import asyncio
import logging
import os

import ollama

logger = logging.getLogger(__name__)

LLM_MODEL = os.getenv("EXAONE_MODEL", "exaone3.5:7.8b")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

_client = ollama.Client(host=OLLAMA_HOST)


def chat_sync(
    messages: list[dict],
    *,
    format: str | None = None,
    options: dict | None = None,
) -> str:
    """EXAONE 동기 chat. 응답 content(strip)를 반환하며, 없으면 빈 문자열."""
    response = _client.chat(model=LLM_MODEL, messages=messages, format=format, options=options)
    return (response.message.content or "").strip()


async def chat(
    messages: list[dict],
    *,
    format: str | None = None,
    options: dict | None = None,
) -> str:
    """EXAONE 비동기 chat (blocking I/O → thread pool)."""
    return await asyncio.to_thread(chat_sync, messages, format=format, options=options)
