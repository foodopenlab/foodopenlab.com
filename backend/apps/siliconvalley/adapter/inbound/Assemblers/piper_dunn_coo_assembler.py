"""DunnCoo — inbound assembler: Schema ↔ DTO."""

from __future__ import annotations

from siliconvalley.adapter.inbound.api.schemas.piper_dunn_coo_schema import DunnCooSchema
from siliconvalley.app.dtos.piper_dunn_coo_dto import DunnCooResponse



def response_to_schema(dto: DunnCooResponse) -> DunnCooSchema:
    return DunnCooSchema(id=dto.id, name=dto.name)
