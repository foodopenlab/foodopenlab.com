from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class YearlyStatRowDTO:
    year: str
    total_incidents: int
    total_patients: int


@dataclass(frozen=True)
class YearlyStatDTO:
    data: List[YearlyStatRowDTO] = field(default_factory=list)


@dataclass(frozen=True)
class AgentStatRowDTO:
    agent: str
    incidents: int
    patients: int


@dataclass(frozen=True)
class AgentStatDTO:
    year: str
    data: List[AgentStatRowDTO] = field(default_factory=list)


@dataclass(frozen=True)
class FacilityStatRowDTO:
    facility: str
    incidents: int
    patients: int


@dataclass(frozen=True)
class FacilityStatDTO:
    year: str
    data: List[FacilityStatRowDTO] = field(default_factory=list)
