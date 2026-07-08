"""RoseModel — domain Entity ↔ ``RoseModelOrm`` persistence."""

from __future__ import annotations

from typing import TYPE_CHECKING

from titanic.adapter.outbound.mappers._types import BookingPersistenceRow
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking

if TYPE_CHECKING:
    from titanic.adapter.outbound.orm.titanic_booking_orm import TitanicBookingOrm as RoseModelOrm


def entity_to_row(entity: RoseBooking) -> BookingPersistenceRow:
    """``RoseBooking`` domain entity → DB upsert row."""
    return entity.to_orm_dict()


def orm_to_entity(orm: RoseModelOrm) -> RoseBooking:
    """``RoseModelOrm`` → ``RoseBooking`` domain entity."""
    entity = RoseBooking.from_upload_row(
        passenger_id=orm.passenger_id,
        pclass=orm.pclass,
        ticket=orm.ticket,
        fare=orm.fare,
        cabin=orm.cabin,
        embarked=orm.embarked,
    )
    if entity is None:
        raise ValueError("RoseModelOrm.passenger_id is required for domain mapping.")
    return entity
