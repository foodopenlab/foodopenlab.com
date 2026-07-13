from __future__ import annotations

import logging
from pathlib import Path

from ontology.app.dtos.face_recognition_dto import (
    FacePrediction,
    FaceRecognitionResult,
    FaceRecognizeQuery,
    FaceTrainCommand,
    FaceTrainResult,
)
from ontology.app.ports.output.face_recognizer_port import IFaceRecognizerPort

logger = logging.getLogger(__name__)

# 이 파일: apps/vision/adapter/outbound/detectors/…  → parents[3] == apps/vision
_RUNS_DIR = Path(__file__).resolve().parents[3] / "resources" / "yolo_train" / "runs"


class UltralyticsFaceRecognizerAdapter(IFaceRecognizerPort):
    """ultralytics YOLO 분류 모델로 파인튜닝·추론을 수행한다. (프레임워크 격리 지점)"""

    def train(self, dataset_root: str, command: FaceTrainCommand) -> FaceTrainResult:
        from ultralytics import YOLO  # 무거운 의존성은 호출 시점에 지연 import

        model = YOLO(command.base_model)
        results = model.train(
            data=dataset_root,
            epochs=command.epochs,
            batch=command.batch,
            imgsz=command.imgsz,
            device=command.device,
            project=str(_RUNS_DIR),
            name="face_recognizer",
            exist_ok=True,
        )
        save_dir = Path(results.save_dir)
        best_weights = save_dir / "weights" / "best.pt"
        class_names = list(getattr(model, "names", {}).values())
        logger.info("[UltralyticsFaceRecognizerAdapter] train 완료 | best=%s classes=%s", best_weights, class_names)
        return FaceTrainResult(
            best_weights_path=str(best_weights),
            epochs_completed=command.epochs,
            save_dir=str(save_dir),
            class_names=class_names,
        )

    def recognize(self, query: FaceRecognizeQuery) -> FaceRecognitionResult:
        from ultralytics import YOLO

        model = YOLO(query.weights_path)
        prediction = model.predict(source=query.image_path, device=query.device, verbose=False)[0]
        names = prediction.names
        probs = prediction.probs
        candidates = [
            FacePrediction(label=names[idx], confidence=float(probs.data[idx]))
            for idx in probs.top5[: query.top_k]
        ]
        logger.info(
            "[UltralyticsFaceRecognizerAdapter] recognize 완료 | top=%s conf=%.3f",
            candidates[0].label,
            candidates[0].confidence,
        )
        return FaceRecognitionResult(image_path=query.image_path, top=candidates[0], candidates=candidates)
