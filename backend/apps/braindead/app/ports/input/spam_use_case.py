from abc import ABC, abstractmethod

from braindead.app.dtos.spam_dto import SpamCheckCommand, SpamResultDTO


class ISpamUseCase(ABC):
    @abstractmethod
    async def check(self, cmd: SpamCheckCommand) -> SpamResultDTO: ...

    @abstractmethod
    async def history(self) -> list[SpamResultDTO]: ...
