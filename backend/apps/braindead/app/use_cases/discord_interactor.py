from braindead.app.dtos.discord_dto import DiscordResultDTO, SendDiscordCommand
from braindead.app.ports.input.discord_use_case import IDiscordUseCase
from braindead.app.ports.output.discord_port import IDiscordPort
from braindead.app.ports.output.llm_port import ILLMPort


class DiscordInteractor(IDiscordUseCase):
    def __init__(self, discord_port: IDiscordPort, llm_port: ILLMPort) -> None:
        self._discord_port = discord_port
        self._llm_port = llm_port

    async def send(self, cmd: SendDiscordCommand) -> DiscordResultDTO:
        body = await self._llm_port.chat(cmd.prompt)
        return await self._discord_port.send(channel=cmd.channel, body=body)
