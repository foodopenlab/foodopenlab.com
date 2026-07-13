# yolo_train — 얼굴 인식(분류) 데이터셋

YOLO **분류(classification)** 학습용 데이터가 흘러 들어오는 폴더입니다.
`LocalYoloFaceDatasetRepository`(Outbound 어댑터)가 이 폴더를 검증하고 학습 파이프라인에 경로를 공급합니다.

## 폴더 구조

```
yolo_train/
├── train/                  ← 학습 split
│   ├── <person_a>/         ← 클래스(인물) = 폴더 이름
│   │   ├── img1.jpg
│   │   └── ...
│   └── <person_b>/
├── val/                    ← 검증 split (동일한 클래스 폴더 구성)
│   ├── <person_a>/
│   └── <person_b>/
└── runs/                   ← 학습 산출물(가중치·그래프). 자동 생성.
```

- **폴더 이름 = 클래스 라벨**입니다. 바운딩박스 `.txt` 라벨은 필요 없습니다.
- 인물을 추가하려면 `train/<새이름>/` 과 `val/<새이름>/` 에 이미지를 넣으면 됩니다. 코드 수정 불필요.
- 현재 예시 데이터: `ben_afflek`, `elton_john`, `jerry_seinfeld`, `madonna`, `mindy_kaling` (5명).

## 사용법

프로젝트 루트(`backend/`)에서 실행합니다.

```bash
# 파인튜닝 (GPU)
python apps/vision/adapter/inbound/cli/face_recognition_cli.py train --epochs 30 --device 0

# 파인튜닝 (GPU 없이 CPU)
python apps/vision/adapter/inbound/cli/face_recognition_cli.py train --epochs 30 --device cpu

# 추론 — 학습된 가중치로 얼굴이 누구인지 인식
python apps/vision/adapter/inbound/cli/face_recognition_cli.py recognize \
    --image apps/vision/resources/yolo_train/val/madonna/<파일>.jpg \
    --weights apps/vision/resources/yolo_train/runs/face_recognizer/weights/best.pt
```

학습이 끝나면 최적 가중치는 `runs/face_recognizer/weights/best.pt` 에 생성됩니다.

## 아키텍처 (Hexagonal)

```
[CLI]  →  IFaceRecognitionUseCase  →  ┌ IFaceDatasetPort   → LocalYoloFaceDatasetRepository (데이터 소스)
(Inbound)   FaceRecognitionInteractor  └ IFaceRecognizerPort → UltralyticsFaceRecognizerAdapter (YOLO)
```

- 데이터 소스를 S3 등으로 바꾸려면 `IFaceDatasetPort` 구현체만 새로 만들어 교체하면 됩니다.
- 기본 모델은 **`yolo11n-cls.pt`**(YOLOv11 Nano 분류, 초경량)입니다. `--base-model yolov8n-cls.pt` 로 바꿀 수도 있습니다.
- **얼굴 탐지(detection)** 로 바꾸려면 바운딩박스 라벨 데이터 + `IFaceRecognizerPort` 대체 어댑터(yolo11n.pt)를 붙이면 됩니다. 유스케이스 코드는 그대로입니다.
