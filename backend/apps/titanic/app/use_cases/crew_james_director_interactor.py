from __future__ import annotations

import logging

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import (
    FileUploadSchema,
    JamesDirectorSchema,
    UploadResultSchema,
)
from titanic.adapter.inbound.mappers.crew_james_director_mapper import file_upload_schemas_to_upload_entities
from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.app.ports.input.crew_james_director_use_case import JamesDirectorUseCase

logger = logging.getLogger("titanic.upload")


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self, repository) -> None:
        self._repository = repository

    async def upload_titanic_file(self, rows: list[FileUploadSchema]) -> UploadResultSchema:
        passengers, bookings = file_upload_schemas_to_upload_entities(rows)
        saved = await self._repository.receive_uploaded_records(passengers, bookings)
        return UploadResultSchema(saved=saved, count=saved)

    async def introduce_myself(self, schema: JamesDirectorSchema) -> JamesDirectorResponse:
        return await self._repository.introduce_myself(
            JamesDirectorQuery(
                id=schema.id,
                name=schema.name,
            )
        )
