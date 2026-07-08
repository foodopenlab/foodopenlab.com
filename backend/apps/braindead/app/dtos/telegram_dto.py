from dataclasses import dataclass


@dataclass
class SendTelegramCommand:
    to: str
    prompt: str


@dataclass
class TelegramResultDTO:
    success: bool
    message: str
