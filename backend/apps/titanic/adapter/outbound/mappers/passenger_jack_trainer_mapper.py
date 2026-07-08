"""JackTrainer — domain Entity ↔ ``JackTrainerOrm`` persistence."""

from __future__ import annotations

from typing import TYPE_CHECKING

from titanic.adapter.outbound.mappers._types import PersonPersistenceRow
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger

if TYPE_CHECKING:
    from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm


def _parse_optional_float(value: str | float | int | None) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = value.strip()
    if not text:
        return None
    return float(text)


def _parse_optional_int(value: str | int | None) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    text = value.strip()
    if not text:
        return None
    return int(float(text))


def entity_to_row(entity: JackPassenger) -> PersonPersistenceRow:
    """``JackPassenger`` domain entity → DB upsert row."""
    return entity.to_orm_dict()


def orm_to_entity(orm: JackTrainerOrm) -> JackPassenger:
    """``JackTrainerOrm`` → ``JackPassenger`` domain entity."""
    entity = JackPassenger.from_upload_row(
        passenger_id=orm.passenger_id,
        name=orm.name,
        gender=orm.gender,
        age=_parse_optional_float(orm.age),
        sib_sp=_parse_optional_int(orm.sib_sp),
        parch=_parse_optional_int(orm.parch),
        survived=orm.survived,
    )
    if entity is None:
        raise ValueError("JackTrainerOrm.passenger_id is required for domain mapping.")
    return entity
