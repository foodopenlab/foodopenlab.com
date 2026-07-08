from pydantic import BaseModel


class JudgeSchema(BaseModel):
    id: int = 0
    name: str = "Judge"
