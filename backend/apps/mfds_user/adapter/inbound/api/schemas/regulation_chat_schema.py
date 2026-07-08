from pydantic import BaseModel


class HistoryItemSchema(BaseModel):
    role: str
    content: str


class RegulationChatRequestSchema(BaseModel):
    message: str
    company_type: str
    history: list[HistoryItemSchema] = []
    session_key: str | None = None


class LawReferenceSchema(BaseModel):
    law_name: str
    article: str = "(조문번호 미상)"


class RegulationChatResponseSchema(BaseModel):
    reply: str
    referenced_laws: list[LawReferenceSchema]
    session_key: str
    message_id: str | None = None
