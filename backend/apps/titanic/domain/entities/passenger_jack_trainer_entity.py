# domain/entities/jack_persona.py
from __future__ import annotations

from abc import abstractmethod

from pydantic import BaseModel

from titanic.domain.value_objects.gender_vo import Gender
from titanic.domain.value_objects.survived_vo import Survived


def _normalize_passenger_id(raw: int | str | None) -> str | None:
    if raw is None:
        return None
    text = str(raw).strip()
    return text or None


class JackPassenger(BaseModel):
    """Jack 승객 row — ``JackTrainerOrm`` (titanic_persons) 업로드·저장용."""

    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    passenger_id: str
    name: str | None
    gender: Gender | None
    age: float | None
    sib_sp: int | None
    parch: int | None
    survived: Survived | None
    gender_raw: str | None = None
    survived_raw: str | None = None

    @classmethod
    def from_upload_row(
        cls,
        *,
        passenger_id: int | str | None,
        name: str | None,
        gender: str | None,
        age: float | None,
        sib_sp: int | None,
        parch: int | None,
        survived: str | None,
    ) -> JackPassenger | None:
        pid = _normalize_passenger_id(passenger_id)
        if pid is None:
            return None
        gender_vo = None
        if gender is not None and str(gender).strip():
            gender_vo = Gender.from_raw(gender)
        return cls(
            passenger_id=pid,
            name=name.strip() if name else None,
            gender=gender_vo,
            age=age,
            sib_sp=sib_sp,
            parch=parch,
            survived=Survived.from_optional_raw(survived),
            gender_raw=gender,
            survived_raw=survived,
        )

    def to_orm_dict(self) -> dict[str, int | float | str | None]:
        return {
            "passenger_id": self.passenger_id,
            "name": self.name,
            "gender": self.gender_raw,
            "age": self.age,
            "sib_sp": self.sib_sp,
            "parch": self.parch,
            "survived": self.survived_raw,
        }


class JackTrainerEntity(BaseModel):
    """JackTrainerPersonaOrm(__abstract__=True) 에 대응하는 도메인 추상 페르소나."""

    model_config = {"frozen": False, "arbitrary_types_allowed": True}

    passenger_id: str
    name: str | None
    gender: Gender | None
    age: float | None
    survived: Survived | None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, JackTrainerEntity):
            return NotImplemented
        return self.passenger_id == other.passenger_id

    def __hash__(self) -> int:
        return hash(self.passenger_id)

    @abstractmethod
    def introduce_myself(self) -> str:
        """페르소나 자기소개 — 구체 클래스에서 반드시 구현."""
        ...

    def is_survived(self) -> bool:
        return self.survived is not None and self.survived.is_survived


class JackIntroducePersona(JackTrainerEntity):
    """introduce_myself 페르소나 구체 구현."""

    catchphrase: str = "I'm the king of the world!"

    def introduce_myself(self) -> str:
        name_str = self.name or "이름 미상"
        survived_str = "생존했습니다" if self.is_survived() else "생존하지 못했습니다"
        return (
            f"안녕하세요, 저는 {name_str}입니다. "
            f"나이는 {self.age if self.age is not None else '미상'}세이고, "
            f"{survived_str}. "
            f"\"{self.catchphrase}\""
        )

    @classmethod
    def from_orm(cls, orm: object) -> JackIntroducePersona:
        gender_raw = getattr(orm, "gender", None)
        gender_vo = Gender.from_raw(gender_raw) if gender_raw else None
        age_raw = getattr(orm, "age", None)
        age = float(age_raw) if age_raw is not None and str(age_raw).strip() else None
        return cls(
            passenger_id=_normalize_passenger_id(getattr(orm, "passenger_id")) or "",
            name=getattr(orm, "name", None),
            gender=gender_vo,
            age=age,
            survived=Survived.from_optional_raw(getattr(orm, "survived", None)),
        )

    def to_orm_dict(self) -> dict:
        return {
            "passenger_id": self.passenger_id,
            "name": self.name,
            "gender": self.gender.value.value if self.gender else None,
            "age": self.age,
            "survived": str(self.survived.value.value) if self.survived else None,
        }
