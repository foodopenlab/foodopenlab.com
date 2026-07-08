from abc import ABC, abstractmethod

from braindead.app.dtos.email_dto import EmailResultDTO, SendEmailCommand


class IEmailUseCase(ABC):
    @abstractmethod
    async def send_email(self, cmd: SendEmailCommand) -> EmailResultDTO: ...
