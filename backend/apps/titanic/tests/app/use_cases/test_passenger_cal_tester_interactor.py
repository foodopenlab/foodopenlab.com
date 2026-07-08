import pandas as pd
import pytest
from unittest.mock import AsyncMock, MagicMock

pytestmark = pytest.mark.asyncio

from titanic.adapter.inbound.api.schemas.passenger_cal_tester_schema import CalTesterSchema
from titanic.app.dtos.passenger_cal_tester_dto import CalTesterQuery, CalTesterResponse
from titanic.app.use_cases.crew_lowe_boat_interactor import LoweBoatInteractor
from titanic.app.use_cases.passenger_cal_tester_interactor import CalTesterInteractor
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
        return_value=CalTesterResponse(id=7, name="Cal Hockley")
    )
    return repo


@pytest.fixture
def interactor(mock_repository):
    return CalTesterInteractor(repository=mock_repository)


class TestTestModel:
    async def test_ranks_trained_strategies(self, interactor):
        lowe = LoweBoatInteractor(repository=MagicMock())
        frame = _sample_train_frame()
        x_all, y_all = lowe.feature_engineering(frame)

        jack = JackTrainerInteractor(repository=MagicMock())
        trained = await jack.train_model(x_all, y_all)

        result = await interactor.test_model(trained)

        assert result["test_samples"] > 0
        assert result["champion"] is not None
        assert result["ranking"][0]["rank"] == 1
        assert result["ranking"][0]["name"] == result["champion"]["name"]

    async def test_introduce_myself(self, interactor, mock_repository):
        schema = CalTesterSchema(id=7, name="Cal Hockley")

        response = await interactor.introduce_myself(schema)

        mock_repository.introduce_myself.assert_called_once_with(
            CalTesterQuery(id=7, name="Cal Hockley")
        )
        assert response == CalTesterResponse(id=7, name="Cal Hockley")
