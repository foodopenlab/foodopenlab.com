from __future__ import annotations

import logging
from typing import Any

import numpy as np
import pandas as pd

from titanic.app.dtos.crew_lowe_boat_dto import LoweBoatQuery, LoweBoatResponse
from titanic.app.ports.input.crew_lowe_boat_use_case import LoweBoatUseCase

logger = logging.getLogger(__name__)


class LoweBoatInteractor(LoweBoatUseCase):

    def __init__(self, repository: Any) -> None:
        self.repository = repository

    async def introduce_myself(self, query: LoweBoatQuery) -> LoweBoatResponse:
        return await self.repository.introduce_myself(query)

    def feature_engineering(
        self, train_set: pd.DataFrame,
    ) -> tuple[list[list[float]], list[int]]:
        train = train_set.copy()
        logger.info("[LoweBoatInteractor] 피처 엔지니어링 시작")

        if "survived" not in train.columns:
            raise ValueError("train_set에 survived 컬럼이 필요합니다.")

        y_series = pd.Series(pd.to_numeric(train["survived"], errors="coerce"))
        if bool(y_series.isna().any()):
            raise ValueError("train_set에 survived 라벨이 없는 행이 있습니다.")
        y_train = y_series.astype(int).tolist()
        train = train.drop("survived", axis=1)

        train["Title"] = train["name"].str.extract(r"([A-Za-z]+)\.", expand=False)
        train["Title"] = train["Title"].replace(
            ["Capt", "Col", "Don", "Dr", "Major", "Rev", "Jonkheer", "Dona", "Mme"], "Rare"
        )
        train["Title"] = train["Title"].replace(["Countess", "Lady", "Sir"], "Royal")
        train["Title"] = train["Title"].replace({"Mlle": "Mr", "Ms": "Miss"})
        title_mapping = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Royal": 5, "Rare": 6}
        train["Title"] = train["Title"].apply(lambda title: title_mapping.get(title, 0))

        train["gender"] = train["gender"].replace({"male": 0, "female": 1})

        bins = [-1, 0, 5, 12, 18, 24, 35, 60, np.inf]
        age_labels = ["Unknown", "Baby", "Child", "Teenager", "Student", "Young Adult", "Adult", "Senior"]
        age_title_mapping = {
            0: "Unknown", 1: "Baby", 2: "Child", 3: "Teenager",
            4: "Student", 5: "Young Adult", 6: "Adult", 7: "Senior",
        }
        age_mapping = {v: k for k, v in age_title_mapping.items()}

        train["age"] = pd.Series(pd.to_numeric(train["age"], errors="coerce")).fillna(-0.5)
        train["AgeGroup"] = pd.Series(pd.cut(train["age"], bins, labels=age_labels)).astype(str)
        mask = train["AgeGroup"] == "Unknown"
        train.loc[mask, "AgeGroup"] = train.loc[mask, "Title"].apply(
            lambda title: age_title_mapping.get(title, "Unknown"),
        )
        train["AgeGroup"] = train["AgeGroup"].replace(age_mapping).fillna(0).astype(int)

        train["embarked"] = train["embarked"].fillna("S").replace({"S": 1, "C": 2, "Q": 3})

        train["fare"] = pd.Series(pd.to_numeric(train["fare"], errors="coerce")).fillna(0)
        train["FareBand"] = (
            pd.Series(pd.qcut(train["fare"], 4, labels=[1, 2, 3, 4], duplicates="drop"))
            .fillna(1)
            .astype(int)
        )

        drop_cols = ["name", "age", "fare", "ticket", "cabin", "passenger_id"]
        train = train.drop(columns=[c for c in drop_cols if c in train.columns])

        x_train = [[float(v) for v in row] for row in train.values.tolist()]
        logger.info("[LoweBoatInteractor] 완료 | samples=%s features=%s", len(x_train), len(x_train[0]) if x_train else 0)
        return x_train, y_train
