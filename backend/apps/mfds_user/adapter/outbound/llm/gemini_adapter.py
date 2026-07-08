import asyncio
import logging
from typing import Optional, Any
from mfds_user.app.ports.output.llm_port import LlmPort
from mfds_user.app.services.settings_service import read_admin_settings

logger = logging.getLogger(__name__)

ExternalApiBudgetExceeded: Any

try:
    from matrix.grid_keymaker_secret_manager import get_keymaker
    from matrix.external_api_budget import ExternalApiBudgetExceeded as _RealException
    ExternalApiBudgetExceeded = _RealException
except ModuleNotFoundError:
    class _KeymakerStub:
        def is_gemini_ready(self) -> bool:
            return False
        def generate_content(self, _message: str) -> str:
            raise RuntimeError("matrix.grid_keymaker_secret_manager is not available")
        def is_quota_error(self, _e: Exception) -> bool:
            return False
    get_keymaker = lambda: _KeymakerStub()
    class _FallbackException(Exception):
        pass
    ExternalApiBudgetExceeded = _FallbackException

class GeminiAdapter(LlmPort):
    def __init__(self) -> None:
        self.km = get_keymaker()

    async def generate_reply(self, message: str, history_lines: list[tuple[str, str]], system_instruction: Optional[str] = None) -> str:
        try:
            return await asyncio.to_thread(self._sync_gemini_reply, message, history_lines, system_instruction)
        except ExternalApiBudgetExceeded as e:
            logger.warning("Gemini budget exceeded: %s", e)
            return "일일 외부 API 호출 예산 한도를 초과했습니다. 어드민 페이지에서 예산을 조정해주세요."
        except Exception as e:
            logger.warning("Gemini API call failed: %s", e)
            if self.km.is_quota_error(e):
                return "Gemini API 무료 할당량을 초과했습니다. 잠시 후 다시 시도해 주세요."
            return f"[AI 응답 생성 실패] {str(e)}"

    def _sync_gemini_reply(self, message: str, history_lines: list[tuple[str, str]], system_instruction: Optional[str] = None) -> str:
        if not self.km.is_gemini_ready():
            raise RuntimeError("GEMINI_API_KEY가 설정되지 않았습니다. com.auditor/.env 를 확인해 주세요.")

        # Read instruction from settings if not explicitly passed
        if not system_instruction:
            settings = read_admin_settings()
            system_instruction = settings.get("prompt_analysis", "")

        hist_str = "\n".join(f"{role}: {text}" for role, text in history_lines if text.strip())
        prompt_parts = []
        if system_instruction:
            prompt_parts.append(system_instruction)
        if hist_str.strip():
            prompt_parts.append("이전 대화:\n" + hist_str)
        prompt_parts.append(f"사용자: {message.strip()}")
        prompt = "\n\n".join(prompt_parts)

        response: Any = self.km.generate_content(prompt)
        try:
            text = (response.text or "").strip()
        except ValueError as e:
            raise RuntimeError(f"응답 텍스트를 읽을 수 없습니다: {e!s}") from e
        
        if not text:
            raise RuntimeError("비어 있는 응답이 반환되었습니다.")
        return text
