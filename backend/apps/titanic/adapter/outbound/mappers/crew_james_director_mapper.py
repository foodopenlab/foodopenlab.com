"""JamesDirector — upload Entity 쌍 → Jack/Rose persistence rows (outbound 조합)."""

from __future__ import annotations

from titanic.adapter.outbound.mappers._types import BookingPersistenceRow, PersonPersistenceRow
from titanic.adapter.outbound.mappers.passenger_jack_trainer_mapper import entity_to_row as jack_entity_to_row
from titanic.adapter.outbound.mappers.passenger_rose_model_mapper import entity_to_row as rose_entity_to_row
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking


def upload_entities_to_persistence_rows(
    passengers: list[JackPassenger],
    bookings: list[RoseBooking],
) -> tuple[list[PersonPersistenceRow], list[BookingPersistenceRow]]:
    """James CSV 업로드 — ``JackPassenger`` + ``RoseBooking`` → ORM upsert rows."""
    persons: list[PersonPersistenceRow] = []
    booking_rows: list[BookingPersistenceRow] = []
    for passenger, booking in zip(passengers, bookings):
        persons.append(jack_entity_to_row(passenger))
        booking_rows.append(rose_entity_to_row(booking))
    return persons, booking_rows
