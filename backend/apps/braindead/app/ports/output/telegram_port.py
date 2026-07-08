from abc import ABC, abstractmethod

from braindead.app.dtos.telegram_dto import TelegramResultDTO


class ITelegramPort(ABC):
    @abstractmethod
    async def send(self, to: str, body: str) -> TelegramResultDTO: ...
