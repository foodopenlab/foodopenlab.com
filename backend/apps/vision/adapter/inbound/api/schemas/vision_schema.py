from pydantic import BaseModel


class VisionSchema(BaseModel):
    id: int = 0
    name: str = "Vision"


class VisionImageUploadResponse(BaseModel):
    id: str
    filename: str
    content_type: str
    size: int


class FacePredictionItem(BaseModel):
    label: str
    confidence: float


class FaceRecognitionResponse(BaseModel):
    filename: str
    label: str
    confidence: float
    candidates: list[FacePredictionItem]
