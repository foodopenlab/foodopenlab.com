from pydantic import BaseModel


class SendEmailRequest(BaseModel):
    to: str
    prompt: str
    to_name: str | None = None


class SendEmailResponse(BaseModel):
    success: bool
    message: str
