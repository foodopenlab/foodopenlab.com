from abc import ABC, abstractmethod

from auth.app.dtos.auth_dto import OAuthProfile
from auth.domain.entities.auth_identity_entity import AuthIdentity


class IIdentityPort(ABC):
    """Driven Port — auth 자체 신원 저장소(auth_identities)."""

    @abstractmethod
    async def upsert_oauth_identity(self, profile: OAuthProfile, roles: list[str]) -> AuthIdentity:
        """(provider, provider_id) 기준 upsert 후 신원 반환. roles는 로그인마다 갱신."""

    @abstractmethod
    async def get(self, identity_id: str) -> AuthIdentity | None:
        """id로 신원 조회(리프레시 시 roles 재로딩)."""
