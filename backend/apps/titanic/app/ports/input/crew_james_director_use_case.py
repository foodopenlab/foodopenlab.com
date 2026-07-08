from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import (
    FileUploadSchema,
    JamesDirectorSchema,
    UploadResultSchema,
)
from titanic.app.dtos.crew_james_director_dto import JamesDirectorResponse


class JamesDirectorUseCase(ABC):

    @abstractmethod
    async def upload_titanic_file(self, rows: list[FileUploadSchema]) -> UploadResultSchema:
        """CSV 파싱 결과를 저장하고 업로드 결과를 반환."""

    @abstractmethod
    async def introduce_myself(self, schema: JamesDirectorSchema) -> JamesDirectorResponse:
        """제임스 감독의 자기소개 메소드."""
