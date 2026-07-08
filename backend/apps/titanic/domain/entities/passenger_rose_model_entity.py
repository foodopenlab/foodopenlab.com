# domain/entities/rose_booking.py
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.fare_vo import Fare
from titanic.domain.value_objects.pclass_vo import PClass

if TYPE_CHECKING:
    from titanic.adapter.outbound.orm.titanic_booking_orm import TitanicBookingOrm as RoseModelOrm


def _normalize_passenger_id(raw: int | str | None) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


class RoseBooking(BaseModel):
    """Rose 예약 도메인 Entity — ``titanic_bookings`` 테이블."""

    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    passenger_id: str
    pclass: PClass | None
    ticket: str | None
    fare: Fare | None
    cabin: Cabin | None
    embarked: str | None = None
    embarked_raw: str | None = None

    def model_post_init(self, __context: object) -> None:
        object.__setattr__(self, "_id_locked", True)

    def __setattr__(self, name: str, value: object) -> None:
        if name == "passenger_id" and getattr(self, "_id_locked", False):
            raise AttributeError("passenger_id는 변경할 수 없습니다.")
        super().__setattr__(name, value)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoseBooking):
            return NotImplemented
        return self.passenger_id == other.passenger_id

    def __hash__(self) -> int:
        return hash(self.passenger_id)

    def __repr__(self) -> str:
        return (
            f"RoseBooking("
            f"id={self.passenger_id!r}, "
            f"pclass={self.pclass!r}, "
            f"embarked={self.embarked!r})"
        )

    def upgrade_class(self, target: PClass) -> None:
        """등급 업그레이드 — 현재보다 높은 등급으로만 변경 가능."""
        if self.pclass is None:
            self.pclass = target
            return
        if target.value.value >= self.pclass.value.value:
            raise ValueError(
                f"upgrade_class는 현재 등급({self.pclass})보다 "
                f"높은 등급으로만 변경 가능합니다. 요청: {target}"
            )
        self.pclass = target

    def is_first_class(self) -> bool:
        return self.pclass is not None and self.pclass.is_first_class

    def has_cabin(self) -> bool:
        return self.cabin is not None

    @classmethod
    def from_upload_row(
        cls,
        *,
        passenger_id: int | str | None,
        pclass: int | str | None,
        ticket: str | None,
        fare: float | str | None,
        cabin: str | None,
        embarked: str | None,
    ) -> RoseBooking | None:
        pid = _normalize_passenger_id(passenger_id)
        if pid is None:
            return None
        ticket_stripped = (ticket or "").strip()
        fare_vo = None
        if fare is not None and str(fare).strip():
            fare_vo = Fare.from_raw(str(fare))
        return cls(
            passenger_id=pid,
            pclass=PClass.from_optional_raw(pclass),
            ticket=ticket_stripped or None,
            fare=fare_vo,
            cabin=Cabin.from_optional_raw(cabin),
            embarked=embarked,
            embarked_raw=embarked,
        )

    @classmethod
    def from_orm(cls, orm: RoseModelOrm) -> RoseBooking:
        """RoseModelOrm → RoseBooking Entity 변환."""
        fare_vo = (
            Fare.from_optional_raw(str(orm.fare))
            if orm.fare is not None and str(orm.fare).strip()
            else None
        )
        return cls(
            passenger_id=_normalize_passenger_id(orm.passenger_id) or "",
            pclass=PClass.from_optional_raw(orm.pclass),
            ticket=orm.ticket or None,
            fare=fare_vo,
            cabin=Cabin.from_optional_raw(orm.cabin),
            embarked=orm.embarked,
            embarked_raw=orm.embarked,
        )

    def to_orm_dict(self) -> dict:
        return {
            "passenger_id": self.passenger_id,
            "pclass": str(self.pclass.value.value) if self.pclass else None,
            "ticket": self.ticket,
            "fare": str(self.fare.value) if self.fare else None,
            "cabin": self.cabin.value if self.cabin else None,
            "embarked": self.embarked_raw,
        }
