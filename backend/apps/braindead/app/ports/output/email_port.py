from abc import ABC, abstractmethod

from braindead.app.dtos.email_dto import EmailResultDTO


class IEmailPort(ABC):
    @abstractmethod
    async def send(self, to: str, subject: str, body: str, to_name: str | None = None) -> EmailResultDTO: ...
