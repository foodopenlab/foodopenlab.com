from abc import ABC, abstractmethod
from uuid import UUID

from mfds_admin.app.dtos.member_dto import MemberDTO


class MemberUseCase(ABC):
    @abstractmethod
    async def list_members(self) -> list[MemberDTO]:
        """가입 회원 목록(승격 여부 포함)."""

    @abstractmethod
    async def promote(self, email: str, admin_id: UUID) -> None:
        """회원을 전문가로 승격 (화이트리스트 추가). 이미 승격이면 무시."""

    @abstractmethod
    async def demote(self, email: str) -> None:
        """전문가 승격 해제 (화이트리스트 제거). 이미 해제면 무시."""
