"""torch 추론 디바이스(GPU/CPU) 자동 선택 — apps/ 전역 공유 인프라."""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)


def resolve_device(preferred: str | None = None) -> str:
    """추론에 사용할 디바이스 문자열을 반환한다.

    우선순위: `preferred` 인자 > `TORCH_DEVICE` 환경변수 > 자동감지.
    자동감지 시 CUDA GPU가 있으면 ``"cuda"``, 없으면 ``"cpu"``.
    """
    explicit = preferred or os.getenv("TORCH_DEVICE")
    if explicit:
        return explicit
    try:
        import torch

        if torch.cuda.is_available():
            return "cuda"
    except Exception as exc:  # torch 미설치·드라이버 문제 등 → CPU 폴백
        logger.warning("[grid_device_manager] CUDA 감지 실패 → cpu 사용 | error=%s", exc)
    return "cpu"
