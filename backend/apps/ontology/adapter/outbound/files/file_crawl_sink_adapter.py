from __future__ import annotations

import asyncio
import json
import logging
import threading
import time
from dataclasses import asdict
from pathlib import Path

from ontology.app.dtos.crawl_dto import CrawlFinding
from ontology.app.ports.output.crawl_sink_port import ICrawlSinkPort

logger = logging.getLogger(__name__)

# apps/ontology/adapter/outbound/files/ → parents[3] == apps/ontology
_ONTOLOGY_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_DIR = _ONTOLOGY_ROOT / "resources" / "crawled"

# 여러 크롤 실행이 겹쳐도 한 줄이 다른 줄과 섞이지 않도록 프로세스 단위 잠금.
_WRITE_LOCK = threading.Lock()


class FileCrawlSinkAdapter(ICrawlSinkPort):
    """크롤러가 찾은 관련 URL을 apps/ontology/resources/crawled/crawled.jsonl 에 append 한다.

    한 줄 = 독립 JSON 객체(JSON Lines). 사용자가 직접 확인·필터링한 뒤
    Redis에 적재하는 원천 파일 역할을 한다.
    """

    def __init__(self, base_dir: Path = _DEFAULT_DIR) -> None:
        self._base_dir = base_dir

    async def save(self, findings: list[CrawlFinding]) -> None:
        if not findings:
            return
        # 파일 I/O(블로킹)는 스레드로 오프로드해 이벤트 루프를 막지 않는다.
        await asyncio.to_thread(self._append_all, findings)

    def _append_all(self, findings: list[CrawlFinding]) -> None:
        saved_at = int(time.time())
        lines = []
        for finding in findings:
            payload = asdict(finding)
            payload["saved_at"] = saved_at
            lines.append(json.dumps(payload, ensure_ascii=False))
        target = self._base_dir / "crawled.jsonl"
        with _WRITE_LOCK:
            self._base_dir.mkdir(parents=True, exist_ok=True)
            with target.open("a", encoding="utf-8") as fp:
                fp.write("\n".join(lines) + "\n")
        logger.info("[FileCrawlSinkAdapter] append %d findings → %s", len(findings), target.name)
