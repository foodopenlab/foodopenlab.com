from abc import ABC, abstractmethod

from auth.app.dtos.auth_dto import TokenBundle
from matrix.grid_seraph_token_guard_manager import TokenPayload


class IAuthUseCase(ABC):
    """Driving Port — 인증 게이트웨이 단일 진입점."""

    @abstractmethod
    async def build_authorize_url(self, provider: str) -> str:
        """소셜 로그인 시작 URL 생성."""

    @abstractmethod
    async def handle_callback(self, provider: str, code: str, state: str) -> TokenBundle:
        """OAuth 콜백 → 신원 upsert → 토큰 발급."""

    @abstractmethod
    async def refresh(self, refresh_token: str) -> TokenBundle:
        """refresh 로테이션 → access 재발급."""

    @abstractmethod
    async def logout(self, current: TokenPayload, refresh_token: str | None) -> None:
        """access jti 블랙리스트 + refresh 폐기."""
