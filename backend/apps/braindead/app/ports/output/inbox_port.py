from abc import ABC, abstractmethod

from braindead.app.dtos.inbox_dto import InboxEmailDTO
from braindead.domain.entities.inbox_entity import InboxEmailEntity


class IInboxPort(ABC):
    @abstractmethod
    async def save(self, entity: InboxEmailEntity) -> InboxEmailDTO: ...

    @abstractmethod
    async def find_all(self) -> list[InboxEmailDTO]: ...
