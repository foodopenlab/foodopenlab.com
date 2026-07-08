from __future__ import annotations

from types import SimpleNamespace
from typing import TYPE_CHECKING, Any, cast

import pytest

from titanic.adapter.outbound.mappers.passenger_jack_trainer_mapper import (
    entity_to_row,
    orm_to_entity,
)
from titanic.domain.entities.passenger_jack_trainer_entity import JackPassenger
from titanic.domain.value_objects.gender_vo import Gender, GenderType
from titanic.domain.value_objects.survived_vo import Survived, SurvivedType

if TYPE_CHECKING:
    from titanic.adapter.outbound.orm.passenger_jack_trainer_orm import JackTrainerOrm


def _make_orm(**overrides: Any) -> JackTrainerOrm:
    row: dict[str, Any] = dict(
        passenger_id="P001",
        name="Dawson, Mr. Jack",
        gender="male",
        age=30.0,
        sib_sp=0,
        parch=0,
        survived="0",
    )
    row.update(overrides)
    return cast("JackTrainerOrm", SimpleNamespace(**row))


def _make_entity(**overrides: Any) -> JackPassenger:
    row: dict[str, Any] = dict(
        passenger_id="P001",
        name="Dawson, Mr. Jack",
        gender="male",
        age=30.0,
        sib_sp=0,
        parch=0,
        survived="0",
    )
    row.update(overrides)
    entity = JackPassenger.from_upload_row(
        passenger_id=row["passenger_id"],
        name=row["name"],
        gender=row["gender"],
        age=row["age"],
        sib_sp=row["sib_sp"],
        parch=row["parch"],
        survived=row["survived"],
    )
    assert entity is not None
    return entity


class TestOrmToEntity:
    def test_maps_passenger_id(self):
        entity = orm_to_entity(_make_orm(passenger_id="P099"))
        assert entity.passenger_id == "P099"

    def test_maps_name(self):
        entity = orm_to_entity(_make_orm(name="Smith, Mr. John"))
        assert entity.name == "Smith, Mr. John"

    def test_maps_gender_male(self):
        entity = orm_to_entity(_make_orm(gender="male"))
        assert entity.gender == Gender(value=GenderType.MALE)

    def test_maps_gender_female(self):
        entity = orm_to_entity(_make_orm(gender="female"))
        assert entity.gender == Gender(value=GenderType.FEMALE)

    def test_maps_age(self):
        entity = orm_to_entity(_make_orm(age=25.0))
        assert entity.age == 25.0

    def test_maps_family_fields(self):
        entity = orm_to_entity(_make_orm(sib_sp=2, parch=3))
        assert entity.sib_sp == 2
        assert entity.parch == 3

    def test_survived_1_maps_to_yes(self):
        entity = orm_to_entity(_make_orm(survived="1"))
        assert entity.survived == Survived(value=SurvivedType.YES)

    def test_survived_0_maps_to_no(self):
        entity = orm_to_entity(_make_orm(survived="0"))
        assert entity.survived == Survived(value=SurvivedType.NO)

    def test_survived_none_maps_to_unknown(self):
        entity = orm_to_entity(_make_orm(survived=None))
        assert entity.survived is None

    def test_none_name_maps_to_none(self):
        entity = orm_to_entity(_make_orm(name=None))
        assert entity.name is None

    def test_missing_passenger_id_raises(self):
        with pytest.raises(ValueError, match="passenger_id is required"):
            orm_to_entity(_make_orm(passenger_id=None))


class TestEntityToRow:
    def test_serializes_core_fields(self):
        row = entity_to_row(
            _make_entity(
                passenger_id="7",
                gender="female",
                age=28.0,
                sib_sp=1,
                parch=0,
                survived="1",
            )
        )

        assert row["passenger_id"] == "7"
        assert row["gender"] == "female"
        assert row["age"] == 28.0
        assert row["sib_sp"] == 1
        assert row["parch"] == 0
        assert row["survived"] == "1"

    def test_survival_unknown_serializes_raw_none(self):
        row = entity_to_row(_make_entity(survived=None))
        assert row["survived"] is None

    def test_none_name_serializes_to_none(self):
        row = entity_to_row(_make_entity(name=None))
        assert row["name"] is None
