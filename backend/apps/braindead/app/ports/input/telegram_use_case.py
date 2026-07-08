from abc import ABC, abstractmethod

from braindead.app.dtos.telegram_dto import SendTelegramCommand, TelegramResultDTO


class ITelegramUseCase(ABC):
    @abstractmethod
    async def send(self, cmd: SendTelegramCommand) -> TelegramResultDTO: ...
