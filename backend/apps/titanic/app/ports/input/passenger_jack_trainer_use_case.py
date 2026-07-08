from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerResponse


class JackTrainerUseCase(ABC):

    @abstractmethod
    async def train_model(
        self,
        x_train: list[list[float]],
        y_train: list[int],
    ) -> dict[str, Any]:
        '''Lowe가 전처리한 (X, y)로 로즈 전략들을 훈련시키는 메소드'''

    @abstractmethod
    async def introduce_myself(self, schema: JackTrainerSchema) -> JackTrainerResponse:
        '''잭 트레이너의 자기소개 메소드'''
