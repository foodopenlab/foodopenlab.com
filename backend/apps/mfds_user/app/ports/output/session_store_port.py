from abc import ABC, abstractmethod
from typing import Optional

from mfds_user.app.dtos.auth_dto import UserSessionDTO


class SessionStorePort(ABC):
    """발급된 세션(JWT) 저장소 + OAuth CSRF state 저장소 (Redis 구현)."""

    @abstractmethod
    async def save(self, session: UserSessionDTO) -> None:
        """access/refresh 토큰으로 조회 가능하도록 세션을 TTL과 함께 저장."""

    @abstractmethod
    async def find_by_refresh_token(self, refresh_token: str) -> Optional[UserSessionDTO]:
        """refresh_token으로 세션 조회 (없거나 만료 시 None)."""

    @abstractmethod
    async def delete_by_access_token(self, access_token: str) -> None:
        """access_token 기준으로 세션(짝 refresh 포함) 삭제 = 로그아웃."""

    @abstractmethod
    async def save_state(self, state: str, provider: str) -> None:
        """OAuth CSRF state를 단기 TTL로 저장."""

    @abstractmethod
    async def consume_state(self, state: str) -> Optional[str]:
        """state를 소비(GET+DEL)하고 저장돼 있던 provider를 반환 (없으면 None)."""
