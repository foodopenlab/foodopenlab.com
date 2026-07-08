from dataclasses import dataclass, field
from typing import Optional, Any
from uuid import UUID

@dataclass(frozen=True)
class ChatHistoryItem:
    role: str
    content: str

@dataclass(frozen=True)
class ChatRequestDTO:
    session_key: str
    message: str
    history: list[ChatHistoryItem] = field(default_factory=list)
    actor_id: Optional[UUID] = None
    actor_type: Optional[str] = None  # 'expert' | 'anonymous'

@dataclass(frozen=True)
class ChatPersistDTO:
    session_key: str
    user_message: str
    assistant_message: str
    query_pattern: str = "law"
    actor_id: Optional[UUID] = None
    actor_type: Optional[str] = None

@dataclass(frozen=True)
class ChatResponseDTO:
    reply: str
    session_key: str
    message_id: Optional[str] = None
