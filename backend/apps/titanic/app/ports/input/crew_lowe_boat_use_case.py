from __future__ import annotations

from abc import ABC, abstractmethod

import pandas as pd

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse


class LoweBoatUseCase(ABC):

    @abstractmethod
    async def introduce_myself(self, query: LoweBoatQuery) -> LoweBoatResponse:
        '''로우 보우트의 자기소개 메소드'''
        pass

    @abstractmethod
    def feature_engineering(
        self, train_set: pd.DataFrame,
    ) -> tuple[list[list[float]], list[int]]:
        '''피처 엔지니어링 — (X, y) 반환'''
