from abc import ABC, abstractmethod


class IGeminiPort(ABC):
    """Driven Port — 외부 LLM(Gemini)에 프롬프트를 보내 응답 텍스트를 받는다."""

    @abstractmethod
    async def generate(self, prompt: str) -> str: ...
