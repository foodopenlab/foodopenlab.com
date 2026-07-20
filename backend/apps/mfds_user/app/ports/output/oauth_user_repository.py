from abc import ABC, abstractmethod

from mfds_user.app.dtos.oauth_dto import OAuthProfile
from mfds_user.domain.entities.user_entity import User


class OAuthUserRepository(ABC):
    @abstractmethod
    async def upsert_social_user(self, profile: OAuthProfile) -> User:
        """소셜 프로필로 유저를 조회/생성(화이트리스트 우회)하고 last_login 갱신."""
