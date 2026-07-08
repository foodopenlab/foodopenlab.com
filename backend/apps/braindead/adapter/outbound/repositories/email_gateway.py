import os
import re

import httpx
import markdown as md

from braindead.app.dtos.email_dto import EmailResultDTO
from braindead.app.ports.output.email_port import IEmailPort


class EmailGateway(IEmailPort):
    def __init__(self) -> None:
        self._webhook_url = os.getenv("N8N_EMAIL_WEBHOOK_URL", "http://n8n:5678/webhook/send-gmail")

    async def send(self, to: str, subject: str, body: str, to_name: str | None = None) -> EmailResultDTO:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                self._webhook_url,
                json={
                    "to": to,
                    "to_name": to_name or to,
                    "subject": _clean_subject(subject),
                    "body": _wrap_html(md.markdown(body)),
                },
            )
        if resp.status_code < 300:
            return EmailResultDTO(success=True, message="발송 완료")
        return EmailResultDTO(success=False, message=f"n8n 오류: {resp.status_code}")


def _clean_subject(text: str) -> str:
    text = re.sub(r"\*{1,3}(.*?)\*{1,3}", r"\1", text)
    text = re.sub(r"^#{1,6}\s*", "", text)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"^제목\s*[:：]\s*", "", text)
    return text.strip()


def _wrap_html(content: str) -> str:
    return (
        '<div style="max-width:600px;font-family:Arial,sans-serif;'
        f'font-size:15px;line-height:1.7;color:#222;">\n{content}\n</div>'
    )
