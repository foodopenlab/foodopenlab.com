from abc import ABC, abstractmethod

from braindead.app.dtos.contact_dto import ContactDTO, UploadContactsCommand, UploadResultDTO


class IContactUseCase(ABC):
    @abstractmethod
    async def upload(self, cmd: UploadContactsCommand) -> UploadResultDTO: ...

    @abstractmethod
    async def list_all(self) -> list[ContactDTO]: ...

    @abstractmethod
    async def search(self, query: str) -> list[ContactDTO]: ...
