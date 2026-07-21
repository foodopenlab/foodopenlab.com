"""HendricksCeo — inbound assembler: Schema ↔ DTO."""

from __future__ import annotations

from siliconvalley.adapter.inbound.api.schemas.piper_hendricks_ceo_schema import HendricksCeoSchema
from siliconvalley.app.dtos.piper_hendricks_ceo_dto import HendricksCeoResponse



def response_to_schema(dto: HendricksCeoResponse) -> HendricksCeoSchema:
    return HendricksCeoSchema(id=dto.id, name=dto.name)
