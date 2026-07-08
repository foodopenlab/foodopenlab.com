"""타이타닉 예약(booking) 영속성 ORM — James 업로드·Jack 조회용 (로즈 ML strategies와 분리)."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from matrix.grid_oracle_database_manager import Base


class TitanicBookingOrm(Base):
    __tablename__ = "titanic_bookings"

    passenger_id: Mapped[str] = mapped_column(
        String(32),
        ForeignKey("titanic_persons.passenger_id", ondelete="CASCADE"),
        primary_key=True,
    )
    pclass: Mapped[int | None] = mapped_column(Integer, nullable=True)
    ticket: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fare: Mapped[float | None] = mapped_column(Float, nullable=True)
    cabin: Mapped[str | None] = mapped_column(String(64), nullable=True)
    embarked: Mapped[str | None] = mapped_column(String(8), nullable=True)
