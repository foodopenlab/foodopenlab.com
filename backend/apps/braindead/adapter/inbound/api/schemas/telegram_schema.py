from pydantic import BaseModel


class SendTelegramRequest(BaseModel):
    to: str
    prompt: str


class SendTelegramResponse(BaseModel):
    success: bool
    message: str
