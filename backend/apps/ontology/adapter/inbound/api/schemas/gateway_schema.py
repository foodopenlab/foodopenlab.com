from pydantic import BaseModel, Field


class GatewayAskRequest(BaseModel):
    question: str = Field(..., description="사용자 질문", min_length=1)


class GatewayAskResponse(BaseModel):
    answer: str
    destination: str
    blocked: bool
