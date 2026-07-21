from dataclasses import dataclass


@dataclass(frozen=True)
class JamesDirectorQuery:
    id: int
    name: str


@dataclass(frozen=True)
class JamesDirectorResponse:
    id: int
    name: str


@dataclass(frozen=True)
class UploadResult:
    saved: int
    count: int
