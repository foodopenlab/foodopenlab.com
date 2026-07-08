from abc import ABC, abstractmethod
from typing import Optional

class LlmPort(ABC):
    @abstractmethod
    async def generate_reply(self, message: str, history_lines: list[tuple[str, str]], system_instruction: Optional[str] = None) -> str:
        """Gemini 모델을 호출하여 답변 생성"""
        pass
