from dataclasses import dataclass


@dataclass
class SendDiscordCommand:
    channel: str
    prompt: str


@dataclass
class DiscordResultDTO:
    success: bool
    message: str
