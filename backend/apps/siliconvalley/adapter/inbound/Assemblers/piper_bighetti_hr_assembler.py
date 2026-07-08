"""BighettiHr — inbound assembler: Schema ↔ DTO."""

from __future__ import annotations

from siliconvalley.adapter.inbound.api.schemas.piper_bighetti_hr_schema import BighettiHrSchema
from siliconvalley.app.dtos.piper_bighetti_hr_dto import BighettiHrQuery, BighettiHrResponse


def schema_to_query(schema: BighettiHrSchema) -> BighettiHrQuery:
    return BighettiHrQuery(id=schema.id, name=schema.name)


def response_to_schema(dto: BighettiHrResponse) -> BighettiHrSchema:
    return BighettiHrSchema(id=dto.id, name=dto.name)
