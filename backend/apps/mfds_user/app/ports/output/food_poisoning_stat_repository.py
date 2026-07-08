from abc import ABC, abstractmethod
from typing import List, Optional

from mfds_user.app.dtos.food_poisoning_stat_dto import (
    AgentStatRowDTO,
    FacilityStatRowDTO,
    YearlyStatRowDTO,
)


class FoodPoisoningStatRepositoryPort(ABC):
    @abstractmethod
    async def get_yearly(self) -> List[YearlyStatRowDTO]: ...

    @abstractmethod
    async def get_by_agent(self, year: Optional[str] = None) -> List[AgentStatRowDTO]: ...

    @abstractmethod
    async def get_by_facility(self, year: Optional[str] = None) -> List[FacilityStatRowDTO]: ...

    @abstractmethod
    async def count_all(self) -> int: ...
