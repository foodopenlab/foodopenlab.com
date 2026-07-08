"""Titanic ORM — Alembic·create_all metadata 등록용."""

from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm
from titanic.adapter.outbound.orm.titanic_booking_orm import TitanicBookingOrm

# 하위 호환 alias (예약 테이블 — 로즈 ML strategies와 분리)
TitanicPerson = JackTrainerOrm
TitanicBooking = TitanicBookingOrm
RoseModelOrm = TitanicBookingOrm

__all__ = [
    "JackTrainerOrm",
    "RoseModelOrm",
    "TitanicBookingOrm",
    "TitanicPerson",
    "TitanicBooking",
]
