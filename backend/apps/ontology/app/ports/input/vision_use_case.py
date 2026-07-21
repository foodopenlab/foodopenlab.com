from abc import ABC, abstractmethod

from ontology.app.dtos.vision_dto import VisionQuery, VisionResponse, VisionUploadResult


class IVisionUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: VisionQuery) -> VisionResponse: ...

    @abstractmethod
    async def upload_image(self, filename: str, content_type: str, content: bytes) -> VisionUploadResult: ...
