from __future__ import annotations

import logging
from pathlib import Path

from vision.app.ports.output.face_dataset_port import IFaceDatasetPort

logger = logging.getLogger(__name__)

# 이 파일: apps/vision/adapter/outbound/repositories/…  → parents[3] == apps/vision
_VISION_ROOT = Path(__file__).resolve().parents[3]
_DATASET_ROOT = _VISION_ROOT / "resources" / "yolo_train"


class LocalYoloFaceDatasetRepository(IFaceDatasetPort):
    """로컬 디렉토리에서 YOLO 분류 데이터셋을 검증하고 루트 경로를 제공한다."""

    def __init__(self, dataset_root: Path = _DATASET_ROOT) -> None:
        self._dataset_root = dataset_root

    def get_dataset_root(self) -> str:
        train_dir = self._dataset_root / "train"
        val_dir = self._dataset_root / "val"
        if not train_dir.is_dir() or not val_dir.is_dir():
            raise FileNotFoundError(f"YOLO 분류 데이터셋 폴더가 없습니다: {train_dir} / {val_dir}")

        classes = sorted(p.name for p in train_dir.iterdir() if p.is_dir())
        if not classes:
            raise FileNotFoundError(f"train 하위에 클래스(인물) 폴더가 없습니다: {train_dir}")

        logger.info("[LocalYoloFaceDatasetRepository] dataset=%s classes=%s", self._dataset_root, classes)
        return str(self._dataset_root)
