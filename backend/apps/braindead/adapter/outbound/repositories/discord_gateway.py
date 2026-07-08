import os

import httpx

from braindead.app.dtos.discord_dto import DiscordResultDTO
from braindead.app.ports.output.discord_port import IDiscordPort


class DiscordGateway(IDiscordPort):
    def __init__(self) -> None:
        self._webhook_url = os.getenv("N8N_DISCORD_WEBHOOK_URL", "http://n8n:5678/webhook/send-discord")

    async def send(self, channel: str, body: str) -> DiscordResultDTO:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self._webhook_url,
                json={"channel": channel, "body": body},
            )
        if resp.status_code < 300:
            return DiscordResultDTO(success=True, message="발송 완료")
        return DiscordResultDTO(success=False, message=f"n8n 오류: {resp.status_code}")
