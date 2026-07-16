from __future__ import annotations

import asyncio
import json
import logging
from pathlib import Path

from ontology.app.ports.output.scout_result_reader_port import IScoutResultReaderPort

logger = logging.getLogger(__name__)

# apps/ontology/adapter/outbound/files/ → parents[3] == apps/ontology
_ONTOLOGY_ROOT = Path(__file__).resolve().parents[3]
_RESOURCES = _ONTOLOGY_ROOT / "resources"

# kind → (하위 폴더, 파일명). FileCrawlSinkAdapter/FileScrapeSinkAdapter의 SINGLE 모드와 일치.
_FILES = {
    "crawled": ("crawled", "crawled.jsonl"),
    "scraped": ("scraped", "scraped.jsonl"),
}


class FileScoutResultReaderAdapter(IScoutResultReaderPort):
    """resources/{crawled,scraped}/*.jsonl 을 읽어 최신순 dict 목록으로 돌려준다."""

    def __init__(self, base_dir: Path = _RESOURCES) -> None:
        self._base = base_dir

    async def read(self, kind: str, limit: int) -> list[dict]:
        return await asyncio.to_thread(self._read, kind, limit)

    def _read(self, kind: str, limit: int) -> list[dict]:
        sub = _FILES.get(kind)
        if sub is None:
            return []
        path = self._base / sub[0] / sub[1]
        if not path.exists():
            return []

        rows: list[dict] = []
        with path.open("r", encoding="utf-8") as fp:
            for line in fp:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    logger.warning("[ScoutResultReader] JSONL 파싱 실패 라인 건너뜀 (%s)", path.name)
        rows.reverse()  # append 순(오래된→최신) → 최신순으로
        return rows[:limit]
