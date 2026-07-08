from abc import ABC, abstractmethod

from braindead.app.dtos.discord_dto import DiscordResultDTO, SendDiscordCommand


class IDiscordUseCase(ABC):
    @abstractmethod
    async def send(self, cmd: SendDiscordCommand) -> DiscordResultDTO: ...
