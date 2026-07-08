from abc import ABC, abstractmethod

from braindead.app.dtos.discord_dto import DiscordResultDTO


class IDiscordPort(ABC):
    @abstractmethod
    async def send(self, channel: str, body: str) -> DiscordResultDTO: ...
