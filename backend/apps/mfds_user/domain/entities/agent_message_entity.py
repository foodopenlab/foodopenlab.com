from dataclasses import dataclass, field
from uuid import UUID
from datetime import datetime
from mfds_user.domain.value_objects.query_pattern_vo import QueryPattern
from mfds_user.domain.value_objects.llm_provider_vo import LLMProvider

@dataclass
class AgentMessage:
    id: UUID
    session_id: UUID
    role: str  # 'user' | 'assistant'
    query_pattern: QueryPattern | None
    content: str
    source_urls: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
