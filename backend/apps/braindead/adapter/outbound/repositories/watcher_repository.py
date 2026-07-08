from __future__ import annotations

import asyncio
import logging
import os

from braindead.app.dtos.watcher_dto import FilterQuery, FilterResult, WatcherQuery, WatcherResponse
from braindead.app.ports.output.watcher_port import IWatcherPort

logger = logging.getLogger(__name__)

_MODEL_NAME = os.getenv("WATCHER_FILTER_MODEL", "beomi/KcELECTRA-base")

_tokenizer = None
_model = None


def _load_model() -> None:
    """KcELECTRA 토크나이저·모델을 프로세스당 1회만 로딩한다 (요청마다 재로딩 방지)."""
    global _tokenizer, _model
    if _model is not None:
        return
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    logger.info("[WatcherRepository] 모델 로딩 시작: %s (HF_HOME=%s)", _MODEL_NAME, os.getenv("HF_HOME"))
    _tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
    # 이진 분류(정상=0, 차단=1) — 분류 헤드는 랜덤 초기화 상태이므로 파인튜닝 전까지는 참고용 스코어다.
    _model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME, num_labels=2)
    _model.eval()
    logger.info("[WatcherRepository] 모델 로딩 완료: %s", _MODEL_NAME)


def _classify_sync(text: str) -> int:
    import torch

    _load_model()
    assert _tokenizer is not None and _model is not None
    inputs = _tokenizer(text, return_tensors="pt", truncation=True, max_length=300)
    with torch.no_grad():
        logits = _model(**inputs).logits
    return int(torch.argmax(logits, dim=-1).item())


class WatcherRepository(IWatcherPort):
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        logger.info("[WatcherRepository] introduce_myself | request=%s", query)
        return WatcherResponse(id=query.id, name=query.name)

    async def filter_email(self, query: FilterQuery) -> FilterResult:
        label = await asyncio.to_thread(_classify_sync, query.text)
        result = FilterResult(label=label, is_normal=(label == 0))
        logger.info("[WatcherRepository] filter_email | label=%s is_normal=%s", label, result.is_normal)
        return result
