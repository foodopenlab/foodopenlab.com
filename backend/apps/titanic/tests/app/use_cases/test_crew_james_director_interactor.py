from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = pytest.mark.asyncio

from titanic.adapter.inbound.api.schemas.crew_james_director_schema import (
    FileUploadSchema,
    JamesDirectorSchema,
)
from titanic.app.dtos.crew_james_director_dto import JamesDirectorQuery, JamesDirectorResponse
from titanic.app.use_cases.crew_james_director_interactor import JamesDirectorInteractor


@pytest.fixture
def mock_repository():
    repo = MagicMock()
    repo.introduce_myself = AsyncMock(
        return_value=JamesDirectorResponse(id=4, name="James Cameron")
    )
    repo.receive_uploaded_records = AsyncMock(return_value=3)
    return repo


@pytest.fixture
def interactor(mock_repository):
    return JamesDirectorInteractor(repository=mock_repository)


def _sample_upload_row(**overrides: str | None) -> FileUploadSchema:
    row = dict(
        passenger_id="1",
        name="Braund, Mr. Owen",
        gender="male",
        age="22",
        sib_sp="1",
        parch="0",
        survived="0",
        pclass="3",
        ticket="A/5 21171",
        fare="7.25",
        cabin=None,
        embarked="S",
    )
    row.update(overrides)
    return FileUploadSchema(**row)


class TestIntroduceMyself:
    async def test_calls_repository_with_correct_query(self, interactor, mock_repository):
        schema = JamesDirectorSchema(id=4, name="James Cameron")

        await interactor.introduce_myself(schema)

        mock_repository.introduce_myself.assert_called_once_with(
            JamesDirectorQuery(id=4, name="James Cameron")
        )

    async def test_returns_repository_response(self, interactor):
        response = await interactor.introduce_myself(
            JamesDirectorSchema(id=4, name="James Cameron")
        )

        assert response == JamesDirectorResponse(id=4, name="James Cameron")


class TestUploadTitanicFile:
    async def test_forwards_mapped_entities_to_repository(self, interactor, mock_repository):
        rows = [
            _sample_upload_row(),
            _sample_upload_row(
                passenger_id="2",
                name="Cumings, Mrs. John",
                gender="female",
                age="38",
                survived="1",
                pclass="1",
                ticket="PC 17599",
                fare="71.28",
                embarked="C",
            ),
        ]

        await interactor.upload_titanic_file(rows)

        passengers, bookings = mock_repository.receive_uploaded_records.await_args.args
        assert len(passengers) == 2
        assert len(bookings) == 2
        mock_repository.receive_uploaded_records.assert_called_once()

    async def test_returns_upload_result_from_repository(self, interactor):
        result = await interactor.upload_titanic_file([_sample_upload_row()])

        assert result.saved == 3
        assert result.count == 3
