from pydantic import BaseModel

from ontology.classification.message_category import MessageCategory


class SpamCheckRequest(BaseModel):
    message: str


class SpamCheckResponse(BaseModel):
    id: int
    category: MessageCategory
    reason: str
    is_spam: bool
