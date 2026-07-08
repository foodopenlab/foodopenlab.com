"""DineshDash — inbound assembler: Schema ↔ DTO."""

from __future__ import annotations

from siliconvalley.adapter.inbound.api.schemas.piper_dinesh_dash_schema import DineshDashSchema
from siliconvalley.app.dtos.piper_dinesh_dash_dto import DineshDashQuery, DineshDashResponse


def schema_to_query(schema: DineshDashSchema) -> DineshDashQuery:
    return DineshDashQuery(id=schema.id, name=schema.name)


def response_to_schema(dto: DineshDashResponse) -> DineshDashSchema:
    return DineshDashSchema(id=dto.id, name=dto.name)
