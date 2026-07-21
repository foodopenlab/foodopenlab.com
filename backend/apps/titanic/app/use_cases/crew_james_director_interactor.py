from __future__ import annotations

import logging

from titanic.app.dtos.crew_james_director_dto import (
    JamesDirectorQuery,
    JamesDirectorResponse,
    UploadResult,
)
from titanic.app.ports.input.crew_james_director_use_case import JamesDirectorUseCase
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.entities.passenger_rose_model_entity import RoseBooking

logger = logging.getLogger("titanic.upload")


class JamesDirectorInteractor(JamesDirectorUseCase):
    def __init__(self, repository) -> None:
        self._repository = repository

    async def upload_titanic_file(
        self, passengers: list[JackPassenger], bookings: list[RoseBooking]
    ) -> UploadResult:
        saved = await self._repository.receive_uploaded_records(passengers, bookings)
        return UploadResult(saved=saved, count=saved)

    async def introduce_myself(self, query: JamesDirectorQuery) -> JamesDirectorResponse:
        return await self._repository.introduce_myself(query)
