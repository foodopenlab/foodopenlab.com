from abc import ABC, abstractmethod

from braindead.app.dtos.contact_dto import ContactDTO, UploadResultDTO
from braindead.domain.entities.contact_entity import ContactEntity


class IContactPort(ABC):
    @abstractmethod
    async def save_all(self, contacts: list[ContactEntity]) -> UploadResultDTO: ...

    @abstractmethod
    async def find_all(self) -> list[ContactDTO]: ...

    @abstractmethod
    async def search(self, query: str) -> list[ContactDTO]: ...
