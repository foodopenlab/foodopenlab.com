from abc import ABC, abstractmethod

from mfds_user.app.dtos.auth_dto import UserSessionDTO


class OAuthUseCase(ABC):
    @abstractmethod
    async def build_authorize_url(self, provider: str) -> str:
        """소셜 로그인 시작 — state 발급·저장 후 제공사 authorize URL 반환."""

    @abstractmethod
    async def handle_callback(self, provider: str, code: str, state: str) -> UserSessionDTO:
        """콜백 — state 검증 → 프로필 조회 → 유저 upsert → JWT 발급 → Redis 저장."""
