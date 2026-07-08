from dataclasses import dataclass, field


@dataclass
class HistoryItem:
    role: str
    content: str


@dataclass
class RegulationChatQuery:
    message: str
    company_type: str
    history: list[HistoryItem] = field(default_factory=list)
    session_key: str | None = None


@dataclass
class LawReference:
    law_name: str
    article: str = "(조문번호 미상)"


@dataclass
class RegulationChatResponse:
    reply: str
    referenced_laws: list[LawReference]
    session_key: str
