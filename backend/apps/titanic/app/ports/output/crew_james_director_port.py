from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking


class JamesDirectorPort(ABC):
    @abstractmethod
    async def receive_uploaded_records(
        self,
        passengers: list[JackPassenger],
        bookings: list[RoseBooking],
    ) -> int:
        ...

    @abstractmethod
    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        """제임스 감독의 자기 소개 레포지토리 추상 메소드."""
        ...
