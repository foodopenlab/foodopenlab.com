from typing import List
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.app.ports.output.whitelist_repository import WhitelistRepositoryPort
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand, WhitelistEntryDTO
from mfds_admin.adapter.outbound.orm.expert_whitelist_orm import ExpertWhitelistORM

class WhitelistInteractor(WhitelistUseCase):
    def __init__(self, whitelist_repository: WhitelistRepositoryPort) -> None:
        self._repo = whitelist_repository

    async def add_to_whitelist(self, command: AddWhitelistCommand) -> WhitelistEntryDTO:
        email = command.email.strip()
        if not email or "@" not in email:
            raise ValueError("올바른 이메일 형식을 입력하세요.")

        existing = await self._repo.get_by_email(email)
        if existing:
            raise ValueError("이미 등록된 이메일입니다.")

        if not command.added_by:
            raise ValueError("등록자를 지정해야 합니다.")

        entry = ExpertWhitelistORM(
            email=email,
            invited_name=command.invited_name,
            role_desc=command.role_desc,
            added_by=command.added_by
        )
        saved = await self._repo.save(entry)

        return WhitelistEntryDTO(
            email=saved.email,
            invited_name=saved.invited_name,
            role_desc=saved.role_desc,
            added_by=saved.added_by,
            added_at=saved.added_at
        )

    async def list_whitelist(self) -> List[WhitelistEntryDTO]:
        entries = await self._repo.list_all()
        return [
            WhitelistEntryDTO(
                email=e.email,
                invited_name=e.invited_name,
                role_desc=e.role_desc,
                added_by=e.added_by,
                added_at=e.added_at
            )
            for e in entries
        ]

    async def remove_from_whitelist(self, email: str) -> None:
        normalized = email.strip()
        if not normalized or "@" not in normalized:
            raise ValueError("올바른 이메일 형식을 입력하세요.")
        deleted = await self._repo.delete_by_email(normalized)
        if not deleted:
            raise ValueError("등록되지 않은 이메일입니다.")
