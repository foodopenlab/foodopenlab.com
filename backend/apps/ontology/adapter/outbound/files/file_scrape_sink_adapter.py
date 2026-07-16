from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from dataclasses import asdict
from enum import Enum
from pathlib import Path

from ontology.app.dtos.scrape_dto import ScrapedItem
from ontology.app.ports.output.scrape_sink_port import IScrapeSinkPort

logger = logging.getLogger(__name__)

# apps/ontology/adapter/outbound/files/ → parents[3] == apps/ontology
_ONTOLOGY_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_DIR = _ONTOLOGY_ROOT / "resources" / "scraped"

# 여러 스크랩 실행이 겹쳐도 한 줄이 다른 줄과 섞이지 않도록 프로세스 단위 잠금.
_WRITE_LOCK = threading.Lock()


class SplitMode(str, Enum):
    """JSONL 출력 파일 분리 방식."""

    SINGLE = "single"  # scraped.jsonl (전부 한 파일에 누적)
    DATE = "date"      # scraped-YYYYMMDD.jsonl (일자별)
    RUN = "run"        # scraped-{실행 타임스탬프}.jsonl (실행 회차별)


class FileScrapeSinkAdapter(IScrapeSinkPort):
    """스크랩 결과를 apps/ontology/resources/scraped/ 아래 JSONL 파일로 append 한다.

    한 줄 = 독립 JSON 객체(JSON Lines). split 모드로 파일 분리 정책을 정한다.
    RUN 모드의 실행 id는 인스턴스 생성 시점에 고정되므로, 한 번의 스크랩 실행
    (=요청당 어댑터 1개)의 결과가 같은 파일에 모인다.
    """

    def __init__(
        self,
        split: SplitMode = SplitMode.SINGLE,
        base_dir: Path = _DEFAULT_DIR,
    ) -> None:
        self._split = split
        self._base_dir = base_dir
        self._run_id = str(int(time.time()))

    async def save(self, item: ScrapedItem) -> None:
        # 파일 I/O(블로킹)는 스레드로 오프로드해 이벤트 루프를 막지 않는다.
        await asyncio.to_thread(self._append, item)

    def _append(self, item: ScrapedItem) -> None:
        payload = asdict(item)
        payload["saved_at"] = int(time.time())
        line = json.dumps(payload, ensure_ascii=False) + "\n"
        target = self._target_path()
        with _WRITE_LOCK:
            self._base_dir.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as fp:
                fp.write(line)
        logger.info("[FileScrapeSinkAdapter] append %s → %s", item.url, target.name)

    def _target_path(self) -> Path:
        if self._split is SplitMode.DATE:
            name = f"scraped-{time.strftime('%Y%m%d')}.jsonl"
        elif self._split is SplitMode.RUN:
            name = f"scraped-{self._run_id}.jsonl"
        else:
            name = "scraped.jsonl"
        return self._base_dir / name
