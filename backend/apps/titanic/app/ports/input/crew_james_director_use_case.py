from __future__ import annotations

from abc import ABC, abstractmethod

from titanic.app.dtos.crew_james_director_dto import (
    JamesDirectorQuery,
    JamesDirectorResponse,
    UploadResult,
)
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking


class JamesDirectorUseCase(ABC):

    @abstractmethod
    async def upload_titanic_file(
        self, passengers: list[JackPassenger], bookings: list[RoseBooking]
    ) -> UploadResult:
        """업로드 엔티티를 저장하고 업로드 결과를 반환."""

    @abstractmethod
    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        """제임스 감독의 자기소개 메소드."""
