from abc import ABC, abstractmethod


class ILLMPort(ABC):
    @abstractmethod
    async def chat(self, message: str) -> str: ...
