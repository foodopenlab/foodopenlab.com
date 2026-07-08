import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

from titanic.adapter.inbound.api.schemas.passenger_jack_trainer_schema import JackTrainerSchema
from titanic.app.dtos.passenger_jack_trainer_dto import JackTrainerQuery, JackTrainerResponse
from titanic.app.use_cases.crew_lowe_boat_interactor import LoweBoatInteractor
from titanic.app.use_cases.passenger_jack_trainer_interactor import JackTrainerInteractor


def _sample_train_frame() -> pd.DataFrame:
    rows = [
        {
            "passenger_id": "1",
            "name": "Braund, Mr. Owen Harris",
            "gender": "male",
            "age": 22.0,
            "sib_sp": 1,
            "parch": 0,
            "pclass": 3,
            "ticket": "A/5 21171",
            "fare": 7.25,
            "cabin": None,
            "embarked": "S",
            "survived": "0",
        },
        {
            "passenger_id": "2",
            "name": "Cumings, Mrs. John Bradley",
            "gender": "female",
            "age": 38.0,
            "sib_sp": 1,
            "parch": 0,
            "pclass": 1,
            "ticket": "PC 17599",
            "fare": 71.28,
            "cabin": "C85",
            "embarked": "C",
            "survived": "1",
        },
        {
            "passenger_id": "3",
            "name": "Heikkinen, Miss. Laina",
            "gender": "female",
            "age": 26.0,
            "sib_sp": 0,
            "parch": 0,
            "pclass": 3,
            "ticket": "STON/O2. 3101282",
            "fare": 7.92,
            "cabin": None,
            "embarked": "S",
            "survived": "0",
        },
        {
            "passenger_id": "4",
            "name": "Futrelle, Mrs. Jacques Heath",
            "gender": "female",
            "age": 35.0,
            "sib_sp": 1,
            "parch": 0,
            "pclass": 1,
            "ticket": "113803",
            "fare": 53.1,
            "cabin": "C123",
            "embarked": "S",
            "survived": "1",
        },
    ]
    # Jack train_test_split(stratify) — 클래스당 최소 2건 이상 필요
    for i in range(5, 21):
        survived = "1" if i % 2 == 0 else "0"
        gender = "female" if i % 2 == 0 else "male"
        rows.append({
            "passenger_id": str(i),
            "name": f"Passenger {i}",
            "gender": gender,
            "age": float(20 + i),
            "sib_sp": 0,
            "parch": 0,
            "pclass": 3,
            "ticket": f"T{i}",
            "fare": 10.0 + i,
            "cabin": None,
            "embarked": "S",
            "survived": survived,
        })
    return pd.DataFrame(rows)


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.introduce_myself = AsyncMock(
        return_value=JackTrainerResponse(id=9, name="Jack Dawson")
    )
    return repo


@pytest.fixture
def interactor(mock_repository):
    return JackTrainerInteractor(repository=mock_repository)


class TestIntroduceMyself:
    async def test_calls_repository_with_correct_query(self, interactor, mock_repository):
        schema = JackTrainerSchema(id=9, name="Jack Dawson")

        await interactor.introduce_myself(schema)

        mock_repository.introduce_myself.assert_called_once_with(
            JackTrainerQuery(id=9, name="Jack Dawson")
        )

    async def test_returns_repository_response(self, interactor):
        schema = JackTrainerSchema(id=9, name="Jack Dawson")

        response = await interactor.introduce_myself(schema)

        assert response == JackTrainerResponse(id=9, name="Jack Dawson")


class TestTrainModel:
    async def test_trains_strategies_from_feature_engineering(self, interactor):
        lowe = LoweBoatInteractor(repository=MagicMock())
        x_all, y_all = lowe.feature_engineering(_sample_train_frame())
        result = await interactor.train_model(x_all, y_all)

        assert result["train_samples"] > 0
        assert len(result["trained_models"]) > 0
        assert len(result["trained_strategies"]) == len(result["trained_models"])
        assert len(result["x_test"]) > 0
        assert len(result["y_test"]) == len(result["x_test"])
