from pydantic import BaseModel, Field


class SemanticAskRequest(BaseModel):
    question: str = Field(..., description="사용자 질문", min_length=1)


class SemanticAskResponse(BaseModel):
    answer: str
    destination: str
    blocked: bool
