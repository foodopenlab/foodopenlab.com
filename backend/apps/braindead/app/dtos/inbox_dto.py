from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReceiveEmailCommand:
    gmail_message_id: str | None
    from_email: str
    from_name: str | None
    subject: str
    body: str
    received_at: datetime | None


@dataclass
class InboxEmailDTO:
    id: int | None
    gmail_message_id: str | None
    from_email: str
    from_name: str | None
    subject: str
    body: str
    received_at: datetime | None
    embedding: list[float] | None = None
