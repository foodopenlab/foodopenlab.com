from abc import ABC, abstractmethod

from braindead.app.dtos.inbox_dto import InboxEmailDTO, ReceiveEmailCommand


class IInboxUseCase(ABC):
    @abstractmethod
    async def receive(self, cmd: ReceiveEmailCommand) -> InboxEmailDTO: ...

    @abstractmethod
    async def list_all(self) -> list[InboxEmailDTO]: ...
