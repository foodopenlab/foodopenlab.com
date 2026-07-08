from pydantic import BaseModel


class ContactResponse(BaseModel):
    id: int
    name: str | None
    email: str | None
    phone: str | None
    company: str | None
    note: str | None


class UploadResultResponse(BaseModel):
    count: int
