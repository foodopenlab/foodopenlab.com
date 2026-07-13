from dataclasses import dataclass


@dataclass
class VisionQuery:
    id: int
    name: str


@dataclass
class VisionResponse:
    id: int
    name: str


@dataclass
class VisionUploadQuery:
    filename: str
    content_type: str
    content: bytes


@dataclass
class VisionUploadResult:
    id: str
    filename: str
    content_type: str
    size: int
