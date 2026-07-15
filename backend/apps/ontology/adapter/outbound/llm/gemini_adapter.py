import asyncio
import logging
from typing import Any

from matrix.grid_keymaker_secret_manager import get_keymaker

from ontology.app.ports.output.gemini_port import IGeminiPort

logger = logging.getLogger(__name__)


class GeminiAdapter(IGeminiPort):
    """
    core/matrix Keymaker를 경유해 GEMINI_API_KEY로 Gemini에 연결한다.

    Keymaker가 키 로딩·모델 폴백(2.5-flash-lite → 2.5-flash → 3.1-flash-lite)·
    외부 API 예산 관리를 담당하므로 여기서는 호출과 텍스트 추출만 한다.
    """

    def __init__(self) -> None:
        self._keymaker = get_keymaker()

    async def generate(self, prompt: str) -> str:
        # 게이트웨이 general 경로의 최종 응답기 — 실패해도 예외를 던지지 않고
        # 안내 문구를 반환한다(감사 로그는 남기고 사용자에겐 500 대신 메시지).
        if not self._keymaker.is_gemini_ready():
            logger.warning("[GeminiAdapter] Gemini 미연결(GEMINI_API_KEY 확인 필요)")
            return "일시적으로 답변할 수 없습니다. (AI 서비스 미연결)"
        try:
            # generate_content는 blocking I/O → thread pool로 오프로드
            response = await asyncio.to_thread(self._keymaker.generate_content, prompt)
        except Exception as exc:
            if self._keymaker.is_quota_error(exc):
                logger.warning("[GeminiAdapter] 할당량 초과: %s", exc)
                return "Gemini API 무료 할당량을 초과했습니다. 잠시 후 다시 시도해 주세요."
            logger.warning("[GeminiAdapter] 호출 실패: %s", exc)
            return "일시적으로 답변을 생성할 수 없습니다. 잠시 후 다시 시도해 주세요."
        return _extract_text(response)


def _extract_text(response: Any) -> str:
    if hasattr(response, "text"):
        text = (response.text or "").strip()
    elif isinstance(response, str):
        text = response.strip()
    else:
        text = ""
    return text or "응답을 생성하지 못했습니다."
