from abc import ABC, abstractmethod

from mfds_admin.app.dtos.member_dto import MemberDTO


class MemberRepositoryPort(ABC):
    @abstractmethod
    async def list_with_promotion(self) -> list[MemberDTO]:
        """가입 회원 전체를 화이트리스트 승격 여부와 함께 반환 (최신 가입순)."""
