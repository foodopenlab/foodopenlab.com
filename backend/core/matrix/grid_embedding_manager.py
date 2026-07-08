"""로컬 Ollama(bge-m3) 텍스트 임베딩 — apps/ 전역 공유 인프라."""

from __future__ import annotations

import asyncio
import logging
import os

import ollama

logger = logging.getLogger(__name__)

_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
_OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
EMBEDDING_DIM = 1024

_client = ollama.Client(host=_OLLAMA_HOST)


def _sync_embed(text: str) -> list[float] | None:
    response = _client.embed(model=_EMBEDDING_MODEL, input=text)
    embeddings = response.embeddings
    if not embeddings:
        return None
    return list(embeddings[0])


async def embed_text(text: str) -> list[float] | None:
    """`text`의 bge-m3 임베딩(1024차원)을 반환합니다. 실패 시 None."""
    stripped = text.strip()
    if not stripped:
        return None
    try:
        return await asyncio.to_thread(_sync_embed, stripped)
    except Exception as exc:
        logger.warning("[grid_embedding_manager] 임베딩 생성 실패 model=%s error=%s", _EMBEDDING_MODEL, exc)
        return None
