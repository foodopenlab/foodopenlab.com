from abc import ABC, abstractmethod


class IOAuthStatePort(ABC):
    """Driven Port — OAuth state(CSRF) 임시 저장."""

    @abstractmethod
    async def save_state(self, state: str, provider: str) -> None: ...

    @abstractmethod
    async def consume_state(self, state: str) -> str | None:
        """state를 1회성으로 소비하고 저장됐던 provider 반환(없으면 None)."""
