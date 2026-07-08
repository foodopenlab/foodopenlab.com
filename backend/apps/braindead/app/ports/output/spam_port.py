from abc import ABC, abstractmethod

from braindead.app.dtos.spam_dto import SpamResultDTO
from braindead.domain.entities.spam_entity import SpamEntity


class ISpamPort(ABC):
    @abstractmethod
    async def save(self, entity: SpamEntity) -> SpamResultDTO: ...

    @abstractmethod
    async def find_all(self) -> list[SpamResultDTO]: ...
