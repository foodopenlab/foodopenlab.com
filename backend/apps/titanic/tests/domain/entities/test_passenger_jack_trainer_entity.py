from types import SimpleNamespace

from titanic.domain.entities.passenger_jack_trainer_entity import JackIntroducePersona, JackPassenger
from titanic.domain.value_objects.gender_vo import Gender, GenderType
from titanic.domain.value_objects.survived_vo import Survived, SurvivedType


class TestJackPassenger:
    def test_from_upload_row_valid(self):
        passenger = JackPassenger.from_upload_row(
            passenger_id=1,
            name="Braund, Mr. Owen Harris",
            gender="male",
            age=22.0,
            sib_sp=1,
            parch=0,
            survived="0",
        )
        assert passenger is not None
        assert passenger.passenger_id == "1"
        assert passenger.name == "Braund, Mr. Owen Harris"
        assert passenger.gender == Gender(value=GenderType.MALE)
        assert passenger.age == 22.0
        assert passenger.sib_sp == 1
        assert passenger.parch == 0
        assert passenger.survived == Survived(value=SurvivedType.NO)

    def test_from_upload_row_none_id(self):
        passenger = JackPassenger.from_upload_row(
            passenger_id=None,
            name="Braund, Mr. Owen Harris",
            gender="male",
            age=22.0,
            sib_sp=1,
            parch=0,
            survived="0",
        )
        assert passenger is None

    def test_to_orm_dict(self):
        passenger = JackPassenger.from_upload_row(
            passenger_id=1,
            name="Braund, Mr. Owen Harris",
            gender="male",
            age=22.0,
            sib_sp=1,
            parch=0,
            survived="0",
        )
        assert passenger is not None
        row = passenger.to_orm_dict()
        assert row["passenger_id"] == "1"
        assert row["name"] == "Braund, Mr. Owen Harris"
        assert row["gender"] == "male"
        assert row["age"] == 22.0
        assert row["sib_sp"] == 1
        assert row["parch"] == 0
        assert row["survived"] == "0"


class TestJackIntroducePersona:
    def test_introduce_myself_survived(self):
        persona = JackIntroducePersona(
            passenger_id="P001",
            name="Dawson, Mr. Jack",
            gender=Gender(value=GenderType.MALE),
            age=20.0,
            survived=Survived(value=SurvivedType.YES),
        )
        intro = persona.introduce_myself()
        assert "Dawson, Mr. Jack" in intro
        assert "20.0" in intro or "20" in intro
        assert "생존했습니다" in intro
        assert "I'm the king of the world!" in intro

    def test_introduce_myself_not_survived(self):
        persona = JackIntroducePersona(
            passenger_id="P001",
            name="Dawson, Mr. Jack",
            gender=Gender(value=GenderType.MALE),
            age=20.0,
            survived=Survived(value=SurvivedType.NO),
        )
        intro = persona.introduce_myself()
        assert "생존하지 못했습니다" in intro

    def test_introduce_myself_name_missing(self):
        persona = JackIntroducePersona(
            passenger_id="P001",
            name=None,
            gender=Gender(value=GenderType.MALE),
            age=None,
            survived=None,
        )
        intro = persona.introduce_myself()
        assert "이름 미상" in intro
        assert "미상" in intro
        assert "생존하지 못했습니다" in intro

    def test_is_survived(self):
        p_yes = JackIntroducePersona(
            passenger_id="1",
            name=None,
            gender=None,
            age=None,
            survived=Survived(value=SurvivedType.YES),
        )
        p_no = JackIntroducePersona(
            passenger_id="2",
            name=None,
            gender=None,
            age=None,
            survived=Survived(value=SurvivedType.NO),
        )
        p_unk = JackIntroducePersona(
            passenger_id="3",
            name=None,
            gender=None,
            age=None,
            survived=None,
        )
        assert p_yes.is_survived() is True
        assert p_no.is_survived() is False
        assert p_unk.is_survived() is False

    def test_equality_and_hash(self):
        p1 = JackIntroducePersona(
            passenger_id="1",
            name=None,
            gender=None,
            age=None,
            survived=Survived(value=SurvivedType.YES),
        )
        p2 = JackIntroducePersona(
            passenger_id="1",
            name=None,
            gender=None,
            age=None,
            survived=Survived(value=SurvivedType.NO),
        )
        p3 = JackIntroducePersona(
            passenger_id="2",
            name=None,
            gender=None,
            age=None,
            survived=Survived(value=SurvivedType.YES),
        )
        assert p1 == p2
        assert p1 != p3
        assert hash(p1) == hash(p2)

    def test_from_orm(self):
        orm = SimpleNamespace(
            passenger_id="P099",
            name="Smith, Mr. John",
            gender="male",
            age=45.0,
            survived="1",
        )
        persona = JackIntroducePersona.from_orm(orm)
        assert persona.passenger_id == "P099"
        assert persona.name == "Smith, Mr. John"
        assert persona.gender == Gender(value=GenderType.MALE)
        assert persona.age == 45.0
        assert persona.survived == Survived(value=SurvivedType.YES)
