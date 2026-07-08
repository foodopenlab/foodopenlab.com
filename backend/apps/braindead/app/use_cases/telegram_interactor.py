from braindead.app.dtos.telegram_dto import SendTelegramCommand, TelegramResultDTO
from braindead.app.ports.input.telegram_use_case import ITelegramUseCase
from braindead.app.ports.output.llm_port import ILLMPort
from braindead.app.ports.output.telegram_port import ITelegramPort


class TelegramInteractor(ITelegramUseCase):
    def __init__(self, telegram_port: ITelegramPort, llm_port: ILLMPort) -> None:
        self._telegram_port = telegram_port
        self._llm_port = llm_port

    async def send(self, cmd: SendTelegramCommand) -> TelegramResultDTO:
        body = await self._llm_port.chat(cmd.prompt)
        return await self._telegram_port.send(to=cmd.to, body=body)
