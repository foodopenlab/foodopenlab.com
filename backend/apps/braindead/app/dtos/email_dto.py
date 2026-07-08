from dataclasses import dataclass


@dataclass
class SendEmailCommand:
    to: str
    prompt: str
    to_name: str | None = None


@dataclass
class EmailResultDTO:
    success: bool
    message: str
