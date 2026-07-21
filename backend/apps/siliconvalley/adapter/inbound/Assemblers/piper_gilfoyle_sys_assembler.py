"""GilfoyleSys — inbound assembler: Schema ↔ DTO."""

from __future__ import annotations

from siliconvalley.adapter.inbound.api.schemas.piper_gilfoyle_sys_schema import GilfoyleSysSchema
from siliconvalley.app.dtos.piper_gilfoyle_sys_dto import GilfoyleSysResponse



def response_to_schema(dto: GilfoyleSysResponse) -> GilfoyleSysSchema:
    return GilfoyleSysSchema(id=dto.id, name=dto.name)
