from __future__ import annotations

import asyncio
import logging
import os

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = "exaone3.5:2.4b"
_DEFAULT_SYSTEM = "당신은 유능한 AI 오케스트레이터입니다. 짧고 명확한 한국어로 답하세요."


class FakerOrchestrator:
    """exaone3.5:2.4b 기반 mid-lane 오케스트레이터."""

    def __init__(
        self,
        model: str | None = None,
        system_prompt: str | None = None,
    ) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL_LOL", _DEFAULT_MODEL)
        self.system_prompt = system_prompt or _DEFAULT_SYSTEM

    def _chat_sync(self, message: str, system: str | None = None) -> str:
        import ollama

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system or self.system_prompt},
                {"role": "user", "content": message},
            ],
        )
        content = response.message.content
        if not content or not content.strip():
            return "응답을 생성하지 못했습니다."
        return content.strip()

    async def chat(self, message: str, system: str | None = None) -> str:
        """Ollama blocking I/O → thread pool."""
        try:
            return await asyncio.to_thread(self._chat_sync, message, system)
        except Exception as exc:
            logger.warning("[FakerOrchestrator] Ollama 실패 | model=%s error=%s", self.model, exc)
            return (
                f"Ollama({self.model})에 연결할 수 없습니다. "
                "로컬 Ollama 실행 및 모델 설치를 확인해 주세요."
            )
