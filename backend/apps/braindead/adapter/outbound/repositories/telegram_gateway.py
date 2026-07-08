import os

import httpx

from braindead.app.dtos.telegram_dto import TelegramResultDTO
from braindead.app.ports.output.telegram_port import ITelegramPort


class TelegramGateway(ITelegramPort):
    def __init__(self) -> None:
        self._webhook_url = os.getenv("N8N_TELEGRAM_WEBHOOK_URL", "http://n8n:5678/webhook/send-telegram")

    async def send(self, to: str, body: str) -> TelegramResultDTO:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self._webhook_url,
                json={"to": to, "body": body},
            )
        if resp.status_code < 300:
            return TelegramResultDTO(success=True, message="발송 완료")
        return TelegramResultDTO(success=False, message=f"n8n 오류: {resp.status_code}")
