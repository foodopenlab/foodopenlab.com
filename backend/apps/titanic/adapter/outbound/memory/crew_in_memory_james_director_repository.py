from __future__ import annotations

import logging
from typing import Any

from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking

logger = logging.getLogger("titanic.upload")


class InMemoryJamesDirectorPort:
    """DB 연결 전 임시 저장소 (요청 스코프에서만 유지)."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []
        self._next_id = 1

    async def receive_uploaded_records(
        self,
        passengers: list[JackPassenger],
        bookings: list[RoseBooking],
    ) -> int:
        records: list[dict[str, Any]] = []
        for passenger, booking in zip(passengers, bookings):
            person_row = passenger.to_orm_dict()
            booking_row = booking.to_orm_dict()
            records.append({**person_row, **booking_row})
        return await self.save_all(records)

    async def save_all(self, records: list[dict[str, Any]]) -> int:
        if not records:
            return 0
        for record in records:
            row = dict(record)
            row.setdefault("id", self._next_id)
            self._next_id += 1
            self._records.append(row)
        logger.info(
            "[titanic-upload][OUTBOUND] memory store ok saved=%s total=%s",
            len(records),
            len(self._records),
        )
        return len(records)

    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        return JamesDirectorResponse(
            id=query.id * 10000,
            name=query.name + "가 메모리 레포지토리에 다녀옴",
        )
