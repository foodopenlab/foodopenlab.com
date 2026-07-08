from datetime import datetime

from pydantic import BaseModel


class ReceiveEmailRequest(BaseModel):
    from_email: str
    from_name: str | None = None
    subject: str
    body: str
    received_at: datetime | None = None
    gmail_message_id: str | None = None


class InboxEmailResponse(BaseModel):
    id: int | None
    gmail_message_id: str | None
    from_email: str
    from_name: str | None
    subject: str
    body: str
    received_at: datetime | None
    filtered: bool = False
