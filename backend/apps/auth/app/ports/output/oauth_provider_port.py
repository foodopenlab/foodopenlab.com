from abc import ABC, abstractmethod

from auth.app.dtos.auth_dto import OAuthProfile


class IOAuthProviderPort(ABC):
    """Driven Port — 소셜 제공사 어댑터 계약 (Strategy). provider별 1 구현."""

    @abstractmethod
    def authorize_url(self, state: str) -> str:
        """사용자를 보낼 제공사 동의(authorize) URL."""

    @abstractmethod
    async def fetch_profile(self, code: str, state: str) -> OAuthProfile:
        """authorization code → 토큰 교환 + userinfo → 정규화된 프로필."""
