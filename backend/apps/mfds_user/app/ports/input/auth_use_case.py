from abc import ABC, abstractmethod
from mfds_user.app.dtos.auth_dto import SignupCommand, LoginCommand, UserSessionDTO

class AuthUseCase(ABC):
    @abstractmethod
    async def signup(self, command: SignupCommand) -> UserSessionDTO:
        """전문가 회원가입 및 첫 세션 반환"""
        pass

    @abstractmethod
    async def login(self, command: LoginCommand) -> UserSessionDTO:
        """전문가 로그인 및 세션 반환"""
        pass

    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> UserSessionDTO:
        """세션 토큰 갱신"""
        pass

    @abstractmethod
    async def logout(self, access_token: str) -> None:
        """로그아웃 및 세션 무효화"""
        pass
