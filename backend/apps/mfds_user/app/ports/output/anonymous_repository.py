from abc import ABC, abstractmethod
from typing import Optional
from mfds_user.app.dtos.anonymous_dto import AnonymousDTO

class AnonymousRepository(ABC):
    @abstractmethod
    async def find_by_cookie_id(self, cookie_id: str) -> Optional[AnonymousDTO]:
        """cookie_id로 비회원 방문자 조회"""
        pass

    @abstractmethod
    async def create_anonymous(self, cookie_id: str) -> AnonymousDTO:
        """비회원 방문자 등록"""
        pass

    @abstractmethod
    async def update_last_seen(self, cookie_id: str) -> AnonymousDTO:
        """비회원 방문자의 last_seen 시각 갱신"""
        pass
