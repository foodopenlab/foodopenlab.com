from abc import ABC, abstractmethod
from typing import List, Optional
from mfds_admin.app.dtos.whitelist_dto import AddWhitelistCommand, WhitelistEntryDTO

class WhitelistRepositoryPort(ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[WhitelistEntryDTO]:
        pass

    @abstractmethod
    async def save(self, command: AddWhitelistCommand) -> WhitelistEntryDTO:
        pass

    @abstractmethod
    async def list_all(self) -> List[WhitelistEntryDTO]:
        pass

    @abstractmethod
    async def delete_by_email(self, email: str) -> bool:
        pass
