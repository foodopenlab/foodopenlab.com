from pydantic import BaseModel


class WatcherSchema(BaseModel):
    id: int = 0
    name: str = "Watcher"


class FilterCheckRequest(BaseModel):
    text: str


class FilterCheckResponse(BaseModel):
    label: int  # 0=정상, 1=차단
    is_normal: bool
