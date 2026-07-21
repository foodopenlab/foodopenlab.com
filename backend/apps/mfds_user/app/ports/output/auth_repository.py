from abc import ABC, abstractmethod
from mfds_user.domain.entities.user_entity import User

class AuthRepository(ABC):
    @abstractmethod
    async def find_all_active(self) -> list[User]:
        """모든 활성 사용자 조회 (일일 리포트 스케줄러 등 배치 대상)"""
        pass
