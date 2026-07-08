"""James Director — ``TitanicRecordSchema`` → domain Entity (inbound adapter 경계)."""

from __future__ import annotations

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import FileUploadSchema, TitanicRecordSchema
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking


def _blank_as_none(value: str | None) -> str | None:
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


def _parse_optional_int(value: str | None) -> int | None:
    text = _blank_as_none(value)
    if text is None:
        return None
    return int(float(text))


def _parse_optional_float(value: str | None) -> float | None:
    text = _blank_as_none(value)
    if text is None:
        return None
    return float(text)


def schema_to_jack_passenger(row: TitanicRecordSchema) -> JackPassenger | None:
    return JackPassenger.from_upload_row(
        passenger_id=_blank_as_none(row.passenger_id),
        name=_blank_as_none(row.name),
        gender=_blank_as_none(row.gender),
        age=_parse_optional_float(row.age),
        sib_sp=_parse_optional_int(row.sib_sb),
        parch=_parse_optional_int(row.parch),
        survived=_blank_as_none(row.survived),
    )


def file_upload_to_jack_passenger(row: FileUploadSchema) -> JackPassenger | None:
    return JackPassenger.from_upload_row(
        passenger_id=_blank_as_none(row.passenger_id),
        name=_blank_as_none(row.name),
        gender=_blank_as_none(row.gender),
        age=_parse_optional_float(row.age),
        sib_sp=_parse_optional_int(row.sib_sp),
        parch=_parse_optional_int(row.parch),
        survived=_blank_as_none(row.survived),
    )


def file_upload_to_rose_booking(row: FileUploadSchema) -> RoseBooking | None:
    return RoseBooking.from_upload_row(
        passenger_id=_blank_as_none(row.passenger_id),
        pclass=_parse_optional_int(row.pclass),
        ticket=_blank_as_none(row.ticket),
        fare=_parse_optional_float(row.fare),
        cabin=_blank_as_none(row.cabin),
        embarked=_blank_as_none(row.embarked),
    )


def file_upload_schemas_to_upload_entities(
    schemas: list[FileUploadSchema],
) -> tuple[list[JackPassenger], list[RoseBooking]]:
    passengers: list[JackPassenger] = []
    bookings: list[RoseBooking] = []
    for row in schemas:
        passenger = file_upload_to_jack_passenger(row)
        if passenger is None:
            continue
        booking = file_upload_to_rose_booking(row)
        if booking is None:
            continue
        passengers.append(passenger)
        bookings.append(booking)
    return passengers, bookings


def schema_to_rose_booking(row: TitanicRecordSchema) -> RoseBooking | None:
    return RoseBooking.from_upload_row(
        passenger_id=_blank_as_none(row.passenger_id),
        pclass=_parse_optional_int(row.pclass),
        ticket=_blank_as_none(row.ticket),
        fare=_parse_optional_float(row.fare),
        cabin=_blank_as_none(row.cabin),
        embarked=_blank_as_none(row.embarked),
    )


def schemas_to_upload_entities(
    schemas: list[TitanicRecordSchema],
) -> tuple[list[JackPassenger], list[RoseBooking]]:
    passengers: list[JackPassenger] = []
    bookings: list[RoseBooking] = []
    for row in schemas:
        passenger = schema_to_jack_passenger(row)
        if passenger is None:
            continue
        booking = schema_to_rose_booking(row)
        if booking is None:
            continue
        passengers.append(passenger)
        bookings.append(booking)
    return passengers, bookings
