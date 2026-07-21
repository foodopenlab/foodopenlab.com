from __future__ import annotations

import asyncio
import io
import logging

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from titanic.app.dtos.crew_hartley_violin_dto import HartleyViolinQuery, HartleyViolinResponse
from titanic.app.ports.input.crew_hartley_violin_use_case import HartleyViolinUseCase
from titanic.app.ports.input.crew_walter_roaster_use_case import WalterRoasterUseCase
from titanic.domain.value_objects.cabin_vo import Cabin
from titanic.domain.value_objects.survival_predictors_vo import SurvivalPredictors

logger = logging.getLogger(__name__)

# SurvivalPredictors + survived 라벨 — Hartley 상관분석 유의미 피처
_CORRELATION_FEATURES = (
    "survived",
    "gender",
    "pclass",
    "fare",
    "cabin",
)

_RATIO_COLUMNS = ("survived", "pclass", "fare")
_DECK_ENCODING = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7}


class HartleyViolinInteractor(HartleyViolinUseCase):

    def __init__(self, repository, walter: WalterRoasterUseCase) -> None:
        self.repository = repository
        self.walter = walter

    async def introduce_myself(self, query: HartleyViolinQuery) -> HartleyViolinResponse:
        '''하틀리 바이올린의 자기소개 인터렉트'''

        return await self.repository.introduce_myself(query)

    def _encode_cabin_deck(self, raw: object) -> int:
        if raw is None or (isinstance(raw, float) and pd.isna(raw)):
            return 0
        cabin = Cabin.from_optional_raw(str(raw))
        if cabin is None:
            return 0
        deck = cabin.deck
        return _DECK_ENCODING.get(deck, 0) if deck else 0

    def _compute_correlation_matrix(self, numeric: pd.DataFrame) -> pd.DataFrame:
        corr = numeric.corr()
        for col in numeric.columns:
            if numeric[col].dropna().nunique() <= 1:
                corr.loc[col, :] = 0.0
                corr.loc[:, col] = 0.0
                corr.loc[col, col] = 1.0
        for row in corr.index:
            for col in corr.columns:
                if pd.isna(corr.loc[row, col]):
                    corr.loc[row, col] = 1.0 if row == col else 0.0
        return corr

    def _prepare_numeric_frame(self, frame: pd.DataFrame) -> pd.DataFrame:
        source = frame.copy()
        numeric = pd.DataFrame(index=source.index)

        for col in _RATIO_COLUMNS:
            if col in source.columns:
                numeric[col] = pd.to_numeric(source[col], errors="coerce")

        if "gender" in source.columns:
            numeric["gender"] = source["gender"].replace({"male": 0, "female": 1})
        if "cabin" in source.columns:
            numeric["cabin"] = source["cabin"].apply(self._encode_cabin_deck)

        ordered = list(_CORRELATION_FEATURES)
        for feature in ordered:
            if feature not in numeric.columns:
                numeric[feature] = float("nan")

        return numeric.loc[:, ordered]

    def _render_correlation_png_sync(self, frame: pd.DataFrame) -> bytes:
        numeric = self._prepare_numeric_frame(frame)
        corr_matrix = self._compute_correlation_matrix(numeric)
        ranking = SurvivalPredictors.correlation_ranking()

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            corr_matrix,
            annot=True,
            cmap="coolwarm",
            fmt=".2f",
            ax=ax,
            xticklabels=_CORRELATION_FEATURES,
            yticklabels=_CORRELATION_FEATURES,
        )
        subtitle = ", ".join(f"{name}({coef:+.2f})" for name, coef in ranking)
        ax.set_title(f"Titanic Feature Correlation\nsurvived ranking: {subtitle}", fontsize=10)
        fig.tight_layout()

        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        plt.close(fig)
        buf.seek(0)
        return buf.read()

    async def get_correlation_heatmap(self) -> bytes:
        '''train set 상관계수 히트맵을 PNG 바이트로 반환합니다.'''
        logger.info("[HartleyViolinInteractor] correlation heatmap 생성 시작")
        train_set = await self.walter.get_train_set()
        return await asyncio.to_thread(self._render_correlation_png_sync, train_set)
