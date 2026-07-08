from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from mfds_user.domain.entities.user_entity import User
from mfds_user.app.dtos.auth_dto import UserSessionDTO

class AuthRepository(ABC):
    @abstractmethod
    async def find_whitelisted_email(self, email: str) -> Optional[dict]:
        """이메일이 화이트리스트에 존재하는지 확인"""
        pass

    @abstractmethod
    async def find_user_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회"""
        pass

    @abstractmethod
    async def get_hashed_password(self, email: str) -> Optional[str]:
        """이메일로 사용자의 해시된 비밀번호 조회"""
        pass

    @abstractmethod
    async def save_user(self, email: str, name: str, password_hash: str, agreed: bool, role: str) -> User:
        """새 사용자 저장"""
        pass

    @abstractmethod
    async def save_session(self, session: UserSessionDTO) -> None:
        """사용자 세션 저장"""
        pass

    @abstractmethod
    async def find_session_by_refresh_token(self, refresh_token: str) -> Optional[UserSessionDTO]:
        """리프레시 토큰으로 세션 조회"""
        pass

    @abstractmethod
    async def delete_session_by_access_token(self, access_token: str) -> None:
        """액세스 토큰으로 세션 삭제 (로그아웃)"""
        pass

    @abstractmethod
    async def update_last_login(self, user_id: UUID) -> None:
        """마지막 로그인 시각 업데이트"""
        pass

    @abstractmethod
    async def find_all_active(self) -> list[User]:
        """모든 활성 사용자 조회"""
        pass
