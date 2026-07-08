from abc import ABC, abstractmethod

from vision.app.dtos.vision_dto import VisionQuery, VisionResponse, VisionUploadQuery, VisionUploadResult


class IVisionPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: VisionQuery) -> VisionResponse: ...

    @abstractmethod
    async def save_image(self, query: VisionUploadQuery) -> VisionUploadResult: ...
