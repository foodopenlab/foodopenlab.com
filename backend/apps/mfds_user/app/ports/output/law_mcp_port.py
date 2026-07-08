from dataclasses import dataclass
from typing import Protocol


@dataclass
class LawSearchResult:
    law_name: str
    law_id: str
    url: str


class LawMcpPort(Protocol):
    async def search_laws(self, query: str) -> list[LawSearchResult]: ...
    async def research_law(self, query: str, task: str = "full_research") -> str | None: ...
