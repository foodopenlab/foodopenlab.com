import asyncio
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from matrix.grid_device_manager import resolve_device

from ontology.adapter.inbound.api.schemas.vision_schema import (
    FacePredictionItem,
    FaceRecognitionResponse,
    VisionImageUploadResponse,
    VisionSchema,
)
from ontology.app.dtos.face_recognition_dto import FaceRecognizeQuery
from ontology.app.dtos.vision_dto import VisionQuery, VisionResponse
from ontology.app.ports.input.face_recognition_use_case import IFaceRecognitionUseCase
from ontology.app.ports.input.vision_use_case import IVisionUseCase
from ontology.dependencies.face_recognition_provider import get_face_recognition_use_case
from ontology.dependencies.vision_provider import get_vision_use_case

router = APIRouter(tags=["vision"])

# 이 파일: apps/vision/adapter/inbound/api/v1/…  → parents[4] == apps/vision
_DEFAULT_WEIGHTS = (
    Path(__file__).resolve().parents[4] / "resources" / "yolo_train" / "runs" / "face_recognizer" / "weights" / "best.pt"
)


@router.get("/vision/myself", response_model=VisionSchema)
async def introduce_myself(
    use_case: IVisionUseCase = Depends(get_vision_use_case),
) -> VisionResponse:
    return await use_case.introduce_myself(VisionQuery(id=0, name="Vision"))


@router.post("/vision/images", response_model=VisionImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_image(
    file: UploadFile = File(...),
    use_case: IVisionUseCase = Depends(get_vision_use_case),
) -> VisionImageUploadResponse:
    content = await file.read()
    try:
        result = await use_case.upload_image(
            filename=file.filename or "unnamed",
            content_type=file.content_type or "application/octet-stream",
            content=content,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return VisionImageUploadResponse(
        id=result.id,
        filename=result.filename,
        content_type=result.content_type,
        size=result.size,
    )


@router.post("/vision/recognize", response_model=FaceRecognitionResponse)
async def recognize_face(
    file: UploadFile = File(...),
    use_case: IFaceRecognitionUseCase = Depends(get_face_recognition_use_case),
) -> FaceRecognitionResponse:
    if not _DEFAULT_WEIGHTS.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="학습된 얼굴 인식 모델(best.pt)이 없습니다. 먼저 파인튜닝을 실행하세요.",
        )
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="빈 파일은 인식할 수 없습니다.")

    suffix = Path(file.filename or "upload.jpg").suffix or ".jpg"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(content)
        tmp.close()
        result = await asyncio.to_thread(
            use_case.recognize,
            FaceRecognizeQuery(image_path=tmp.name, weights_path=str(_DEFAULT_WEIGHTS), device=resolve_device(), top_k=3),
        )
    finally:
        Path(tmp.name).unlink(missing_ok=True)

    return FaceRecognitionResponse(
        filename=file.filename or "upload",
        label=result.top.label,
        confidence=result.top.confidence,
        candidates=[FacePredictionItem(label=c.label, confidence=c.confidence) for c in result.candidates],
    )
