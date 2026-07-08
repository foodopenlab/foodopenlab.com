from dataclasses import dataclass


@dataclass
class JudgeQuery:
    id: int
    name: str


@dataclass
class JudgeResponse:
    id: int
    name: str
