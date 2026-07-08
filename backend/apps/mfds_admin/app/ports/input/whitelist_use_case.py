from abc import ABC, abstractmethod
from typing import List
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand, WhitelistEntryDTO

class WhitelistUseCase(ABC):
    @abstractmethod
    async def add_to_whitelist(self, command: AddWhitelistCommand) -> WhitelistEntryDTO:
        pass

    @abstractmethod
    async def list_whitelist(self) -> List[WhitelistEntryDTO]:
        pass

    @abstractmethod
    async def remove_from_whitelist(self, email: str) -> None:
        pass
