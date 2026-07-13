from pathlib import Path

from ontology.adapter.inbound.api.schemas.vision_schema import VisionSchema
from ontology.app.dtos.vision_dto import VisionQuery, VisionResponse, VisionUploadQuery, VisionUploadResult
from ontology.app.ports.input.vision_use_case import IVisionUseCase
from ontology.app.ports.output.vision_port import IVisionPort

ALLOWED_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"}


class VisionInteractor(IVisionUseCase):
    def __init__(self, port: IVisionPort) -> None:
        self._port = port

    async def introduce_myself(self, schema: VisionSchema) -> VisionResponse:
        return await self._port.introduce_myself(VisionQuery(id=schema.id, name=schema.name))

    async def upload_image(self, filename: str, content_type: str, content: bytes) -> VisionUploadResult:
        if not content:
            raise ValueError("빈 파일은 업로드할 수 없습니다.")
        extension = Path(filename).suffix.lower()
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValueError(f"지원하지 않는 이미지 확장자입니다: {extension or '(없음)'}")
        return await self._port.save_image(
            VisionUploadQuery(filename=filename, content_type=content_type, content=content)
        )
