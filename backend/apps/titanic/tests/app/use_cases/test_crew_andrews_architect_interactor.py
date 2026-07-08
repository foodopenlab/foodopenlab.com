import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

from titanic.adapter.outbound.repositories.crew_andrews_architect_repository import (
    AndrewsArchitectRepository,
)
from titanic.app.use_cases.crew_andrews_architect_interactor import AndrewsArchitectInteractor


def _sample_train_frame() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"gender": "male", "age": 33.0, "survived": "0"},
            {"gender": "male", "age": 34.0, "survived": "1"},
            {"gender": "male", "age": 31.0, "survived": "0"},
            {"gender": "female", "age": 33.0, "survived": "1"},
        ]
    )


@pytest.fixture
def interactor():
    return AndrewsArchitectInteractor(repository=AndrewsArchitectRepository())


class TestComposeChatReply:
    async def test_demographic_survival_rate(self, interactor):
        reply = await interactor.compose_chat_reply(
            "33살 남성의 생존율",
            train_set=_sample_train_frame(),
            train_stats={"total": 4, "survived": 2, "deceased": 2, "survival_rate": 50.0},
            trained={"train_samples": 3, "trained_models": ["KNN"]},
            scores={"champion": {"name": "KNN", "accuracy": 0.83}},
        )

        assert "33세 전후" in reply
        assert "남성" in reply
        assert "생존율" in reply
        assert "KNN" not in reply

    async def test_feature_importance_question(self, interactor):
        reply = await interactor.compose_chat_reply(
            "생존율에 중요한 것이 뭐야?",
            train_set=_sample_train_frame(),
            train_stats={"total": 4, "survived": 2, "deceased": 2, "survival_rate": 50.0},
            trained={"train_samples": 3, "trained_models": ["KNN"]},
            scores={"champion": {"name": "KNN", "accuracy": 0.83}},
        )

        assert "상관" in reply
        assert "성별" in reply
        assert "KNN" not in reply

    async def test_statistics_intent(self, interactor):
        reply = await interactor.compose_chat_reply(
            "승객 통계 알려줘",
            train_set=_sample_train_frame(),
            train_stats={"total": 891, "survived": 342, "deceased": 549, "survival_rate": 38.4},
            trained={"train_samples": 712, "trained_models": ["KNN"]},
            scores={"champion": {"name": "KNN", "accuracy": 0.83}},
        )

        assert "891" in reply
        assert "38.4" in reply
