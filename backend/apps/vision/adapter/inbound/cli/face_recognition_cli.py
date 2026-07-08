"""사람 얼굴 인식(분류) 파인튜닝·추론 CLI — Inbound Driving Adapter.

사용 예:
  python apps/vision/adapter/inbound/cli/face_recognition_cli.py train --epochs 30 --device 0
  python apps/vision/adapter/inbound/cli/face_recognition_cli.py recognize \
      --image some_face.jpg \
      --weights apps/vision/resources/yolo_train/runs/face_recognizer/weights/best.pt
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

# apps/ 를 sys.path 에 추가해 vision 을 최상위 패키지로 import (main.py / conftest.py 와 동일 부트스트랩)
_BACKEND_DIR = Path(__file__).resolve().parents[5]
for _p in (_BACKEND_DIR / "core", _BACKEND_DIR / "apps"):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from vision.app.dtos.face_recognition_dto import FaceRecognizeQuery, FaceTrainCommand  # noqa: E402
from vision.dependencies.face_recognition_provider import get_face_recognition_use_case  # noqa: E402


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="YOLO 얼굴 인식(분류) 파인튜닝·추론")
    sub = parser.add_subparsers(dest="command", required=True)

    t = sub.add_parser("train", help="파인튜닝 실행")
    t.add_argument("--base-model", default="yolo11n-cls.pt")
    t.add_argument("--epochs", type=int, default=30)
    t.add_argument("--batch", type=int, default=16)
    t.add_argument("--imgsz", type=int, default=224)
    t.add_argument("--device", default="0", help="GPU 인덱스(0) 또는 cpu")

    r = sub.add_parser("recognize", help="얼굴 인식(추론) 실행")
    r.add_argument("--image", required=True)
    r.add_argument("--weights", required=True)
    r.add_argument("--device", default="0")
    r.add_argument("--top-k", type=int, default=3)

    args = parser.parse_args()
    use_case = get_face_recognition_use_case()

    if args.command == "train":
        result = use_case.train(
            FaceTrainCommand(
                base_model=args.base_model,
                epochs=args.epochs,
                batch=args.batch,
                imgsz=args.imgsz,
                device=args.device,
            )
        )
        print(f"✅ 학습 완료 | best={result.best_weights_path}")
        print(f"   클래스: {result.class_names}")
        print(f"   결과 폴더: {result.save_dir}")
    else:
        result = use_case.recognize(
            FaceRecognizeQuery(
                image_path=args.image,
                weights_path=args.weights,
                device=args.device,
                top_k=args.top_k,
            )
        )
        print(f"✅ 인식 결과 | {result.image_path}")
        print(f"   → {result.top.label} ({result.top.confidence:.1%})")
        for candidate in result.candidates[1:]:
            print(f"      {candidate.label} ({candidate.confidence:.1%})")


if __name__ == "__main__":
    main()
