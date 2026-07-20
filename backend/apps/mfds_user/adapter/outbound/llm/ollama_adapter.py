import asyncio
import logging
from typing import Optional

from matrix.grid_exaone_llm_manager import LLM_MODEL, chat_sync

from mfds_user.app.ports.output.llm_port import LlmPort
from mfds_user.app.services.settings_service import read_admin_settings

logger = logging.getLogger(__name__)


class OllamaAdapter(LlmPort):
    def __init__(self) -> None:
        self._model = LLM_MODEL  # 로깅용

    async def generate_reply(
        self,
        message: str,
        history_lines: list[tuple[str, str]],
        system_instruction: Optional[str] = None,
    ) -> str:
        try:
            return await asyncio.to_thread(self._sync_reply, message, history_lines, system_instruction)
        except Exception as exc:
            logger.warning("[OllamaAdapter] 실패 model=%s error=%s", self._model, exc)
            return f"Ollama({self._model})에 연결할 수 없습니다. 로컬 Ollama 실행 및 모델 설치를 확인해 주세요."

    def _sync_reply(
        self,
        message: str,
        history_lines: list[tuple[str, str]],
        system_instruction: Optional[str] = None,
    ) -> str:
        if not system_instruction:
            settings = read_admin_settings()
            system_instruction = settings.get("prompt_analysis", "")

        messages: list[dict] = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        for role, content in history_lines:
            if content.strip():
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": message})

        return chat_sync(messages) or "응답을 생성하지 못했습니다."
