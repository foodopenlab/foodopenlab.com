from pydantic import BaseModel


class SendDiscordRequest(BaseModel):
    channel: str
    prompt: str


class SendDiscordResponse(BaseModel):
    success: bool
    message: str
