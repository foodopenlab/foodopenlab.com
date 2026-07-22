# 물체 감지 (Object Detection) 가이드 — SSD를 넘어서

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 과거 **SSD(Single Shot Detector)** 기반 검출기를 최신 모델로 대체하고, 멀티에이전트 구성요소로 사용
> 짝 문서: `video-qlora-multiagent-guide.md`(동영상), `image-classification-transfer-learning-guide.md`(이미지 분류)
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **SSD는 단일단(single-shot) 검출기의 원조**다. 그 현대적 후계자가 **YOLO 계열**이고, 트랜스포머 쪽 대안이 **RT-DETR / RF-DETR**이다.
- **8GB에서 학습·추론 모두 편하다.** YOLO n/s/m 변형은 여유롭게 파인튜닝된다.
- **추천 3갈래:**
  - 실전 기본값(빠르고 쉬움) → **YOLO26** (또는 안정적 베이스라인 **YOLO11**)
  - 정확도·가려짐·도메인시프트 → **RF-DETR / RT-DETR** (NMS-free 트랜스포머)
  - **라벨 없이 텍스트로 지시** → **YOLO-World / Grounding DINO** (오픈 보캐블러리 = 에이전트 친화)
- **핵심 툴:** **Ultralytics**(YOLO 원커맨드) + **supervision/Roboflow**(데이터·후처리) + **SAHI**(소형 객체) + ONNX/TensorRT(배포).
- **전이학습 원칙:** COCO 사전학습 가중치 → 커스텀 클래스 파인튜닝. 데이터 적으면 백본 freeze + 강한 증강.

---

## 1. 8GB VRAM 현실 점검 (검출 편)

| 작업 | Nano/Small | Medium | Large / DETR-R50 |
|---|---|---|---|
| 추론(640px) | ✅ 실시간 | ✅ | ✅ |
| 파인튜닝(640px) | ✅ 배치 16~32 | ✅ 배치 8~16 | ⚠️ 배치↓ / AMP / freeze |
| 고해상도(1280px) | ✅ | ⚠️ 배치↓ | ⚠️ |
| 오픈보캐블러리 추론 | ✅ (YOLO-World) | ✅ | Grounding DINO는 무겁지만 추론 가능 |

- 검출은 분류보다 헤드가 무겁지만, **YOLO 소형 변형은 8GB에 매우 잘 맞는다.** Ampere라 **AMP(bf16/fp16)** 로 배치·속도를 벌 수 있다.
- OOM이면: 배치↓ → 이미지 크기↓ → 백본 일부 freeze 순으로 후퇴.

---

## 2. 모델 추천

### 2-1. 실전 기본값: YOLO26 (또는 YOLO11)
- **YOLO26 (Ultralytics, 2026년 초):** NMS 제거·DFL 제거로 **엔드투엔드 배포가 간결**하고, 엣지(n/s)에서 특히 강하다. CoreML/TFLite 내보내기가 매끄러움.
- **YOLO11:** 여전히 널리 쓰이는 **안정적 베이스라인**. 기존 YOLO 파이프라인·스크립트를 재활용하기 좋다.
- **SSD 대체 관점:** 둘 다 단일단 검출기 계보라 SSD를 **거의 드롭인**으로 대체하면서 정확도·속도·사용성이 크게 향상.
- **크기 선택(8GB):** 프로토타입은 **n/s**, 정확도 필요하면 **m**.

### 2-2. 정확도·강건성: RF-DETR / RT-DETR
- **RF-DETR:** 2026년 지도학습 검출에서 선두권(COCO mAP ~54.7%, 저지연). **가려짐·복잡 장면·도메인 시프트**에 강해 정밀 애플리케이션의 실용적 기본값.
- **RT-DETR / v2 / v3 / v4, D-FINE, DEIM:** 트랜스포머 기반 실시간 검출기. **NMS-free**로 후처리가 단순하고 수렴이 빠른 편. R18/R50 스케일은 8GB에서 파인튜닝 가능.
- **언제:** 소형/겹친 객체가 많거나, YOLO로 정확도 천장에 부딪혔을 때.

### 2-3. 오픈 보캐블러리 (에이전트 친화): YOLO-World / Grounding DINO
- **텍스트 프롬프트로 검출** — 라벨링된 데이터 없이 "빨간 헬멧", "넘어진 사람" 같은 임의 대상을 찾는다.
- **에이전트 관점:** 오케스트레이터가 자연어로 검출 대상을 지시 → 재학습 없이 대응(이른바 **agentic object detection**). 멀티에이전트에서 가장 유연.
- **트레이드오프:** 정밀도가 필요한 좁은 도메인은 여전히 지도학습 검출기가 유리. **오픈보캐블러리로 1차 탐지 → 필요 시 전용 모델 파인튜닝**의 2단 전략을 권장.

### 2-4. 고전 유지가 필요하면 (torchvision)
- `torchvision`에 **SSD / SSDlite / Faster R-CNN / RetinaNet / FCOS** 사전학습 모델이 내장. 기존 SSD 코드를 유지·비교하려면 여기서 시작하되, 신규 프로젝트는 위 최신 모델을 권장.

### 2-5. 비교 요약

| 모델 | 유형 | 후처리 | 8GB 파인튜닝 | 강점 | 에이전트 적합성 |
|---|---|---|---|---|---|
| **YOLO26** | 단일단(NMS-free) | 없음 | ✅ | 속도·배포·엣지 | ★★ |
| **YOLO11** | 단일단 | NMS | ✅ | 안정·생태계 | ★★ |
| **RF-DETR / RT-DETR** | 트랜스포머 | 없음 | ⚠️ 소형만 | 정확도·가려짐 | ★★ |
| **YOLO-World** | 오픈보캐블러리 | NMS | ⚠️ | 텍스트 지시·무라벨 | ★★★ |
| **Grounding DINO** | 오픈보캐블러리 | 없음 | ⚠️ 무거움 | 제로샷 정확도 | ★★★ |
| torchvision SSD | 단일단(고전) | NMS | ✅ | 레거시 호환 | ★ |

---

## 3. 전이학습 & 데이터 전략

### 3-1. 파인튜닝 흐름
1. **COCO 사전학습 가중치**에서 출발(전이학습 기본).
2. 커스텀 데이터로 파인튜닝. 데이터가 적으면 **백본 일부 freeze**(Ultralytics `freeze` 인자) + 강한 증강.
3. 클래스 수·객체 크기 분포에 맞춰 이미지 크기·앵커(구형 YOLO/SSD) 조정. 최신 모델은 앵커-프리라 이 부담이 적다.

### 3-2. 데이터·라벨 스킬
- **포맷:** YOLO(txt) / COCO(json) / Pascal VOC(xml). 툴 간 변환 필요(`supervision`, Roboflow).
- **주석 도구:** Roboflow, CVAT, Label Studio.
- **소형 객체:** 이미지 크기↑ 또는 **SAHI(Slicing Aided Hyper Inference)** 로 타일 분할 추론/학습.
- **클래스 불균형:** 희소 클래스 오버샘플링, copy-paste 증강, 손실 가중.

### 3-3. 증강·정규화(대부분 Ultralytics 내장)
- **Mosaic, MixUp, Copy-Paste, HSV 지터, 스케일/플립.** Mosaic은 소형·다객체에 특히 효과적(단, 학습 말기 몇 에폭은 끄는 게 정석 — `close_mosaic`).
- 과적합 시: 증강↑, 에폭↓, 백본 freeze↑.

### 3-4. 임계값·평가 스킬
- **추론 임계값:** confidence·IoU(NMS) 튜닝으로 정밀도/재현율 균형. NMS-free 모델은 conf만 조정.
- **지표:** **mAP@50**, **mAP@50–95**(주지표), 클래스별 P/R, PR 커브. 검증셋 기준 early stopping.
- **TTA / 앙상블:** 필요 시 정확도 소폭 향상.

---

## 4. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 핵심: YOLO 학습/검증/내보내기 원커맨드
pip install ultralytics

# 데이터셋·후처리·시각화 (박스/트래킹/필터)
pip install supervision

# 소형 객체용 슬라이싱 추론/학습
pip install sahi

# 트랜스포머·오픈보캐블러리 검출 (RT-DETR, Grounding DINO, OWL-ViT 등)
pip install transformers

# 배포 (경량·고속)
pip install onnx onnxruntime-gpu
#  TensorRT는 NVIDIA 채널로 별도 설치 시 추가 가속

# (선택) 종합 프레임워크: RTMDet·DETR 계열 다수
#  pip install mmengine mmcv mmdet   # 설정 복잡, 필요 시만
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 검출 학습 | **Ultralytics(YOLO)** | 학습·검증·추적·내보내기 원커맨드 (필수) |
| 데이터·후처리 | **supervision / Roboflow** | 포맷 변환·주석·박스 필터·트래킹 |
| 소형 객체 | **SAHI** | 슬라이싱 추론으로 작은 객체 검출 |
| 트랜스포머/제로샷 | **Transformers** | RT-DETR, Grounding DINO, OWL-ViT, YOLOS |
| 종합 | MMDetection | RTMDet·DETR 다수(무겁지만 강력) |
| 레거시 | torchvision | SSD·Faster R-CNN 등 고전 baseline |
| 배포 | ONNX Runtime / TensorRT | 경량·고속 추론, 에이전트 툴화 |

---

## 5. 코드 스켈레톤

### 5-1. YOLO 전이학습 (Ultralytics)

```python
from ultralytics import YOLO

model = YOLO("yolo26s.pt")        # COCO 사전학습에서 출발 (또는 yolo11s.pt)

model.train(
    data="dataset.yaml",          # 클래스·train/val 경로 정의
    epochs=100,
    imgsz=640,
    batch=16,                     # 8GB 기준. OOM이면 낮추기
    amp=True,                     # Ampere 혼합정밀 (VRAM 절감)
    freeze=10,                    # 데이터 적을 때 백본 앞 10개 레이어 freeze
    close_mosaic=10,              # 마지막 10에폭 mosaic off
    optimizer="AdamW", lr0=1e-3,
    project="runs", name="custom_det",
)

metrics = model.val()             # mAP@50, mAP@50-95
model.export(format="onnx")       # 배포용 내보내기 (또는 engine=TensorRT)
```

### 5-2. 오픈 보캐블러리 검출 (텍스트 프롬프트)

```python
from ultralytics import YOLOWorld

model = YOLOWorld("yolov8s-world.pt")
model.set_classes(["forklift", "person without helmet", "spilled liquid"])
results = model.predict("scene.jpg", conf=0.25)
# → 라벨링 데이터 없이 텍스트로 지정한 대상 검출
```

### 5-3. 소형 객체 (SAHI 슬라이싱)

```python
from sahi import AutoDetectionModel
from sahi.predict import get_sliced_prediction

det = AutoDetectionModel.from_pretrained(
    model_type="ultralytics", model_path="runs/custom_det/weights/best.pt",
    confidence_threshold=0.3, device="cuda:0")
result = get_sliced_prediction("large_scene.jpg", det,
    slice_height=640, slice_width=640,
    overlap_height_ratio=0.2, overlap_width_ratio=0.2)
```

---

## 6. 멀티에이전트 통합

- **검출 에이전트로 래핑:** 입력=이미지, 출력=`[{"class","bbox","conf"}, ...]` JSON.
- **오픈보캐블러리로 지시 수용:** 오케스트레이터가 자연어로 대상 지정 → YOLO-World/Grounding DINO가 재학습 없이 검출(agentic detection). 정밀도가 필요해지면 그 클래스만 전용 YOLO로 파인튜닝.
- **다른 문서와의 파이프라인:**
  - **동영상 편**과 연계: 비디오 키프레임 → 검출 → (`supervision`) ByteTrack 등으로 **객체 추적**.
  - **이미지 분류 편**과 연계: 검출로 객체를 크롭 → 이미지 분류기로 세부 라벨 정제 → VLM으로 장면 추론.
- **경량 배포:** ONNX/TensorRT로 상시 로드. 검출기는 가벼워 다중 상주 가능.
- **라우팅:** conf 임계값 + 클래스별 캘리브레이션으로 오탐 관리, 애매하면 상위 에이전트로 에스컬레이션.

---

## 7. 함정 체크리스트

- [ ] 데이터 라벨 포맷·경로 불일치 → "학습은 되는데 mAP 0". `dataset.yaml`과 실제 파일 검증.
- [ ] Mosaic을 끝까지 켜둠 → 후반 불안정. `close_mosaic`로 말기 비활성.
- [ ] 소량 데이터에 전체 파인튜닝 → 과적합. `freeze` + 증강.
- [ ] 소형 객체를 640px 그대로 → 놓침. 해상도↑ 또는 SAHI.
- [ ] 배치만 키우다 OOM → AMP 켜고 imgsz/batch 조정.
- [ ] mAP@50만 보고 만족 → **mAP@50–95**와 클래스별 P/R 확인.
- [ ] 오픈보캐블러리로 정밀 검출 기대 → 좁은 도메인은 지도학습 파인튜닝이 필요.

---

## 8. 파일명 추천

- **1순위 (영문):** `object-detection-ssd-guide.md` *(현재 파일명)*
- 대안:
  - `object-detection-yolo-rtdetr-rtx3060ti.md`
  - `detection-agent-setup.md`
  - 한글 선호 시: `물체감지_SSD_가이드.md`

> 세트 구성: `video-qlora-multiagent-guide.md` + `image-classification-transfer-learning-guide.md` + `object-detection-ssd-guide.md` → 멀티에이전트 비전 스택 문서 묶음.