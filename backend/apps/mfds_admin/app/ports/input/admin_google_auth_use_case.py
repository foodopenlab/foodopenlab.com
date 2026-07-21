from abc import ABC, abstractmethod

from mfds_admin.app.dtos.admin_auth_dto import AdminTokenDTO


class AdminGoogleAuthUseCase(ABC):
    @abstractmethod
    async def login_with_google(self, email: str, name: str) -> AdminTokenDTO:
        """구글 인증 이메일이 허용 목록이면 어드민 JWT를 발급한다."""
        pass
