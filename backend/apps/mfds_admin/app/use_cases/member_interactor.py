from uuid import UUID

from mfds_admin.app.dtos.member_dto import MemberDTO
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand
from mfds_admin.app.ports.input.member_use_case import MemberUseCase
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.app.ports.output.member_repository import MemberRepositoryPort


class MemberInteractor(MemberUseCase):
    """회원 목록 조회 + 승격/강등. 승격/강등은 화이트리스트 use case를 재사용한다."""

    def __init__(
        self,
        member_repository: MemberRepositoryPort,
        whitelist_use_case: WhitelistUseCase,
    ) -> None:
        self._members = member_repository
        self._whitelist = whitelist_use_case

    async def list_members(self) -> list[MemberDTO]:
        return await self._members.list_with_promotion()

    async def promote(self, email: str, admin_id: UUID) -> None:
        try:
            await self._whitelist.add_to_whitelist(
                AddWhitelistCommand(
                    email=email,
                    invited_name=None,
                    role_desc="관리자 승격",
                    added_by=admin_id,
                )
            )
        except ValueError as exc:
            # 이미 승격된 경우는 성공으로 간주(멱등), 그 외 검증 오류만 전파.
            if "이미" not in str(exc):
                raise

    async def demote(self, email: str) -> None:
        try:
            await self._whitelist.remove_from_whitelist(email)
        except ValueError:
            # 이미 강등/미등록이면 무시(멱등).
            pass
