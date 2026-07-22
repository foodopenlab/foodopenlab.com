from abc import ABC, abstractmethod

from auth.app.dtos.auth_dto import IssuedAccessToken


class ITokenIssuerPort(ABC):
    """Driven Port — access token 발급(개인키). 구현은 outbound 어댑터에만 존재한다."""

    @abstractmethod
    def issue_access_token(
        self, sub: str, roles: list[str], aud: str, email: str = "", name: str = ""
    ) -> IssuedAccessToken: ...
