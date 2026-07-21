from dataclasses import dataclass
from pydantic import BaseModel


@dataclass(frozen=True)
class ChatMessage:
    role: str
    text: str


@dataclass(frozen=True)
class ChatCommand:
    messages: list[ChatMessage]
    system_instruction: str | None = None


@dataclass(frozen=True)
class SmithCaptainQuery:
    id: int
    name: str


@dataclass(frozen=True)
class SmithCaptainResponse:
    id: int
    name: str


class ChatResponse(BaseModel):
    text: str