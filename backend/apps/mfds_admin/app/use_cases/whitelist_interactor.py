from dataclasses import replace
from typing import List
from mfds_admin.app.ports.input.whitelist_use_case import WhitelistUseCase
from mfds_admin.app.ports.output.whitelist_repository import WhitelistRepositoryPort
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand, WhitelistEntryDTO

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

        # ORM 생성은 어댑터(repo)의 책임 — 정규화한 이메일만 넘긴다.
        return await self._repo.save(replace(command, email=email))

    async def list_whitelist(self) -> List[WhitelistEntryDTO]:
        return await self._repo.list_all()

    async def remove_from_whitelist(self, email: str) -> None:
        normalized = email.strip()
        if not normalized or "@" not in normalized:
            raise ValueError("올바른 이메일 형식을 입력하세요.")
        deleted = await self._repo.delete_by_email(normalized)
        if not deleted:
            raise ValueError("등록되지 않은 이메일입니다.")
