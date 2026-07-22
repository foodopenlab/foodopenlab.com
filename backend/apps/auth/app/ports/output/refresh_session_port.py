from abc import ABC, abstractmethod

from auth.app.dtos.auth_dto import RefreshRotation


class IRefreshSessionPort(ABC):
    """Driven Port — refresh 세션 영속화(로테이션·재사용 감지·jti 블랙리스트)."""

    @abstractmethod
    async def start(self, sub: str) -> str:
        """새 세션 시작 → 새 refresh 토큰 반환."""

    @abstractmethod
    async def rotate(self, refresh_token: str) -> RefreshRotation:
        """refresh 토큰 로테이션. 재사용 감지 시 해당 sub 세션 전체 폐기 후 예외."""

    @abstractmethod
    async def revoke(self, refresh_token: str) -> None:
        """단일 refresh 토큰 폐기(로그아웃)."""

    @abstractmethod
    async def blacklist_jti(self, jti: str, ttl_seconds: int) -> None:
        """access token jti를 만료 시점까지 즉시차단 목록에 등록."""

    @abstractmethod
    async def is_jti_blacklisted(self, jti: str) -> bool:
        """jti가 즉시차단 목록에 있는지 조회."""
