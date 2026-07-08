from abc import ABC, abstractmethod

from vision.adapter.inbound.api.schemas.vision_schema import VisionSchema
from vision.app.dtos.vision_dto import VisionResponse, VisionUploadResult


class IVisionUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: VisionSchema) -> VisionResponse: ...

    @abstractmethod
    async def upload_image(self, filename: str, content_type: str, content: bytes) -> VisionUploadResult: ...
