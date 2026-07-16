from __future__ import annotations

from ontology.app.dtos.scout_dto import ScoutResultsView
from ontology.app.ports.input.scout_results_use_case import IScoutResultsUseCase
from ontology.app.ports.output.scout_result_reader_port import IScoutResultReaderPort

_KINDS = ("crawled", "scraped")
_MAX_LIMIT = 1000


class ScoutResultsInteractor(IScoutResultsUseCase):
    """resources 결과 파일을 읽어 조회용 뷰로 돌려준다."""

    def __init__(self, reader: IScoutResultReaderPort) -> None:
        self._reader = reader

    async def list(self, kind: str, limit: int) -> ScoutResultsView:
        if kind not in _KINDS:
            raise ValueError(f"지원하지 않는 결과 종류입니다: {kind}")
        bounded = max(1, min(limit, _MAX_LIMIT))
        items = await self._reader.read(kind, bounded)
        return ScoutResultsView(kind=kind, items=items)
