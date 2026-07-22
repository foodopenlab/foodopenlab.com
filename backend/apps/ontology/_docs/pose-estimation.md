# 자세 추정 (Pose Estimation) 가이드 — OpenPose를 넘어서

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 과거 **OpenPose** 기반 자세 추정을 최신 모델로 대체하고, 멀티에이전트 구성요소로 사용
> 짝 문서: `video-qlora-multiagent-guide.md`(동영상) · `image-classification-transfer-learning-guide.md`(이미지 분류) · `object-detection-ssd-guide.md`(물체 감지) · `semantic-segmentation-pspnet-guide.md`(시멘틱 분할)
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **OpenPose는 상향식(bottom-up) + 전신(몸·손·얼굴) 다인 추정의 원조**다. 느리고 정확도가 최신 모델에 뒤진다. 필요에 따라 갈아타면 된다.
- **8GB 현실:** 자세 추정은 **이 시리즈에서 가장 가볍다.** RTMPose는 GTX 1660Ti에서 430+ FPS → 3060 Ti면 학습·추론 모두 넉넉.
- **추천(용도별):**
  - 실전 실시간 기본값 → **RTMPose** (또는 검출+포즈 단일패스 **YOLO26-Pose**)
  - 최고 정확도 → **ViTPose++** (top-down)
  - **전신(손·얼굴) = OpenPose의 상징 기능** → **DWPose / RTMW**
  - 상향식·군중·단일패스 → **RTMO / YOLO26-Pose** (OpenPose식이되 훨씬 빠름)
  - 온디바이스/모바일 → **MediaPipe / MoveNet**
- **핵심 연결:** 자세 추정 → 키포인트 시퀀스 → **행동 인식**(동영상 편의 3DCNN 대체와 직접 연결).
- **핵심 툴:** **MMPose**(RTMPose·ViTPose·DWPose·RTMW 총망라) + **Ultralytics**(YOLO-pose) + MediaPipe + Transformers(ViTPose).

---

## 1. 8GB VRAM 현실 점검 (자세 편)

| 모델 | 8GB 학습 | 8GB 추론 | 비고 |
|---|---|---|---|
| **RTMPose (s/m)** | ✅ 여유 | ✅ 초고속 | 실시간 기본값 |
| **YOLO26-Pose (n/s/m)** | ✅ | ✅ | 검출+포즈 단일패스 |
| **RTMO** | ✅ | ✅ | 원스테이지 다인 |
| **ViTPose (S/B)** | ✅ | ✅ | 정확도 우수 |
| **ViTPose-L/H** | ⚠️ 배치↓ | ✅ | 최고 정확도, 무거움 |
| **DWPose / RTMW (전신)** | ✅ | ✅ | 133 키포인트 |
| 3D 메시(SMPL-X) | ⚠️ 소형만 | ✅ | 무거운 편 |

- 자세 추정은 **사람 크롭(top-down) 또는 히트맵/좌표 회귀**라 분할·검출보다 메모리 부담이 작다. **8GB에서 대부분 편하게 학습**된다.
- Ampere라 **AMP** 로 속도·배치를 더 벌 수 있다.

---

## 2. top-down vs bottom-up (OpenPose에서 오는 사람에게 중요)

- **Bottom-up (OpenPose식):** 모든 관절을 먼저 찾고 사람 단위로 묶음. **검출기 불필요**, 군중에서 인원수에 둔감. 단, 결합 로직이 복잡.
  - 현대 대안: **RTMO / YOLO26-Pose** (원스테이지, 훨씬 빠르고 정확).
- **Top-down:** 사람 검출 → 크롭마다 포즈 추정. **정확도 우위**(RTMPose·ViTPose). 사람 수가 많으면 크롭 수만큼 비용 증가.
  - 파이프라인: **사람 검출기(RTMDet-tiny 또는 YOLO-person) → 포즈 모델 → 추적.**
- **선택 가이드:** 군중·저지연·검출기 없음 → 상향식/단일패스. 정확도·소수 인원 → top-down. **물체 감지 편의 검출기를 그대로 재사용**하면 top-down이 자연스럽다.

---

## 3. 모델 추천

### 3-1. 실전 실시간 기본값: RTMPose (또는 YOLO26-Pose)
- **RTMPose (MMPose):** **SimCC 헤드**(좌표를 분류로 처리)로 정확도·속도 균형이 탁월. RTMPose-m ≈ 75.8% AP(COCO), 상용 하드웨어에서 실시간. 커먼 하드웨어에서 돌리는 사실상 표준.
- **YOLO26-Pose (Ultralytics):** **검출 박스 + 17 키포인트를 단일패스**로. 분류·검출·분할·포즈·OBB를 한 아키텍처로 통합 → 엣지·실시간에 최적. 원커맨드 학습.
- **8GB 선택:** 프로토타입 **s**, 정확도 필요 시 **m**.

### 3-2. 최고 정확도: ViTPose / ViTPose++
- 평범한 **ViT 백본**으로 키포인트 추정. **ViTPose++** 는 다중 데이터셋(COCO·AIC·MPII·CrowdPose) 동시 학습으로 SOTA.
- ViTPose-S ≈ 75.8 AP, L ≈ 78.3, H ≈ 80.9 AP. 스포츠 분석·의료 모션캡처처럼 **정확도가 최우선**일 때. GPU 필요(3060 Ti에서 S/B 여유).

### 3-3. 전신(몸·손·얼굴): DWPose / RTMW ← OpenPose 전신의 직접 후계
- **DWPose:** RTMPose에 **2단 distillation + UBody 데이터**로 전신(133 키포인트) 성능 강화.
- **RTMW:** 실시간 **2D·3D 전신**. PAFPN·HEM으로 손·얼굴·발 등 미세 부위 해상도·정확도 향상.
- **OpenPose를 쓰던 이유가 전신이었다면 여기로 갈아타는 게 정답.**

### 3-4. 상향식·군중: RTMO / DETRPose / RF-DETR Keypoint
- **RTMO:** 원스테이지 실시간 다인. top-down 급 정확도를 단일패스 속도로.
- **DETRPose / RF-DETR Keypoint:** 2025년 이후 등장한 **트랜스포머 실시간 다인 포즈**. Pose Denoising으로 수렴·강건성 개선, 일부 지표에서 YOLO11-X 상회.

### 3-5. 온디바이스/모바일: MediaPipe / MoveNet
- **MediaPipe(BlazePose):** 33 키포인트(손·발 포함), 온디바이스 30+ FPS, iOS/Android/Web. 카메라 프레임이 기기를 벗어나지 않아 **프라이버시** 이점.
- **MoveNet / PoseNet:** TF.js/TFLite로 웹·모바일 17 키포인트.

### 3-6. 비교 요약

| 모델 | 방식 | 키포인트 | 8GB 학습 | 강점 | 에이전트 적합성 |
|---|---|---|---|---|---|
| **RTMPose** | top-down | 17/133 | ✅ | 속도·정확 균형 | ★★ |
| **YOLO26-Pose** | 단일패스 | 17 | ✅ | 검출+포즈 통합·엣지 | ★★ |
| **ViTPose++** | top-down | 17 | ✅(S/B) | 최고 정확도 | ★★ |
| **DWPose / RTMW** | top-down | 133(전신) | ✅ | 손·얼굴 포함 | ★★★ |
| **RTMO** | bottom-up | 17 | ✅ | 군중·단일패스 | ★★ |
| **MediaPipe** | top-down | 33 | (경량) | 온디바이스·프라이버시 | ★★ |

---

## 4. 키포인트 스키마 · 손실 · 전이학습 · 데이터 스킬

> "모델 선택은 더 이상 어려운 부분이 아니다. **키포인트 스키마·가려짐 처리·평가·데이터 라벨링**이 진짜 병목이다."

### 4-1. 키포인트 스키마 (가장 중요)
- 표준: **COCO 17(몸)**, **전신 133**(몸+손+얼굴+발), MPII 16. 커스텀이면 **좌우 대칭 쌍·연결(skeleton)·부모 관계**를 처음에 명확히 정의.
- 스키마가 바뀌면 사전학습 헤드를 교체하고 재학습.

### 4-2. 데이터
- **COCO keypoint 포맷** + **가시성 플래그**(0=미라벨, 1=라벨됐으나 가려짐, 2=보임).
- **양:** 사전학습 모델을 커스텀 스키마로 파인튜닝 시 **5,000~10,000 인스턴스**부터 유용. 새 도메인 처음부터면 **50,000+** 필요.
- 주석 도구: CVAT, Label Studio, COCO Annotator.

### 4-3. 증강 — 치명적 함정 주의
- **Flip 시 좌우 키포인트 인덱스를 스왑**해야 함(왼쪽 손목↔오른쪽 손목). 안 하면 조용히 성능 붕괴. **이게 자세 추정 최다 실수.**
- 그 외: 회전, 스케일, half-body 크롭, 색상 지터.

### 4-4. 손실 & 헤드
- **히트맵 MSE**(가우시안): 고전·정확, 고해상도 필요.
- **SimCC(좌표 분류, RTMPose)**: 경량·빠름.
- **좌표 회귀 + OKS 손실(YOLO-pose)**: 단일패스.

### 4-5. 평가 지표
- **OKS 기반 AP/AR(COCO)** 이 주지표. **PCK**(정확도 임계), 3D는 **MPJPE / PA-MPJPE**.

### 4-6. 영상 처리 스킬
- **추적:** ByteTrack 등으로 프레임 간 사람 ID 유지.
- **스무딩:** **One-Euro 필터**로 떨림(jitter) 제거 — 실시간 스켈레톤 품질의 핵심.

---

## 5. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 검출+포즈 단일패스, 원커맨드
pip install ultralytics

# 온디바이스/모바일 실시간
pip install mediapipe

# ViTPose 등 트랜스포머 포즈
pip install transformers

# 키포인트 시각화·추적·후처리
pip install supervision

# 배포
pip install onnx onnxruntime-gpu

# 종합 프레임워크: RTMPose·RTMO·ViTPose·DWPose·RTMW 총망라 (권장)
#  pip install mmengine mmcv mmpose mmdet   # 설정 다소 복잡하나 가장 강력
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 종합 포즈 | **MMPose** | RTMPose·RTMO·ViTPose·DWPose·RTMW 전부, MMDeploy로 다양한 백엔드 |
| 단일패스 | **Ultralytics(YOLO-pose)** | 검출+포즈, 원커맨드 학습·내보내기 |
| 온디바이스 | **MediaPipe / MoveNet** | 모바일·웹 실시간, 프라이버시 |
| 트랜스포머 | Transformers | ViTPose 즉시 사용 |
| 검출기(top-down) | RTMDet-tiny / YOLO-person | 사람 박스 제공 |
| 추적·후처리 | supervision + One-Euro | ID 유지·스무딩 |
| 배포 | ONNX Runtime / TensorRT | 경량·고속 |

---

## 6. 코드 스켈레톤

### 6-1. YOLO-pose 전이학습 (Ultralytics)

```python
from ultralytics import YOLO

model = YOLO("yolo26s-pose.pt")     # COCO 사전학습
model.train(
    data="pose_dataset.yaml",       # 키포인트 수·flip 쌍 정의
    epochs=100, imgsz=640, batch=16, amp=True,
    freeze=10,                      # 데이터 적으면 백본 앞부분 freeze
)
model.val()                         # OKS AP/AR
model.export(format="onnx")
```

### 6-2. ViTPose 추론 (Transformers, top-down)

```python
from transformers import AutoProcessor, VitPoseForPoseEstimation
# 1) 사람 검출(YOLO/RTMDet)로 bbox 확보
# 2) 각 bbox 크롭을 ViTPose에 입력 → 키포인트
proc = AutoProcessor.from_pretrained("usyd-community/vitpose-base-simple")
model = VitPoseForPoseEstimation.from_pretrained("usyd-community/vitpose-base-simple")
# inputs = proc(image, boxes=person_boxes, ...); outputs = model(**inputs)
```

### 6-3. MediaPipe 실시간 (온디바이스)

```python
import mediapipe as mp
pose = mp.solutions.pose.Pose(model_complexity=1)
# results = pose.process(rgb_frame); results.pose_landmarks  # 33 keypoints
```

---

## 7. 멀티에이전트 통합

- **자세 에이전트로 래핑:** 입력=이미지/프레임, 출력=`[{person_id, bbox, keypoints:[(x,y,conf)...]}]` JSON.
- **검출기 재사용(top-down):** `object-detection` 에이전트의 사람 bbox → 포즈 모델에 크롭 입력. 검출·포즈 파이프라인 공유.
- **★ 자세 → 행동 인식(동영상 편과 직접 연결):** 프레임별 키포인트를 시퀀스로 모아 **시간 모델(ST-GCN, MotionBERT 등)** 에 넣으면 행동 인식. 이는 **동영상 분류(3DCNN 대체)** 를 **포즈 기반**으로 구현하는 대안 경로 — VLM 대비 경량·해석 용이.
- **분할 편과 연계:** 사람 마스크 + 스켈레톤으로 정밀 인물 이해.
- **다운스트림:** 낙상 감지, 제스처, 스포츠·재활 각도 분석, 작업 자세(ergonomics).
- **영상:** 추적 + One-Euro 스무딩으로 안정적 스켈레톤, VLM이 자세·행동을 자연어로 해석.
- **라우팅:** 키포인트 신뢰도 낮거나 가려짐 심하면 상위 에이전트/전신 모델(DWPose)로 에스컬레이션.

---

## 8. 함정 체크리스트

- [ ] **Flip 증강 시 좌우 키포인트 스왑 누락** → 조용한 성능 붕괴(최다 실수).
- [ ] 가시성 플래그(0/1/2) 무시 → 가려진 관절 학습 왜곡.
- [ ] 커스텀 스키마인데 사전학습 헤드 그대로 → 재학습 필요.
- [ ] top-down인데 사람 검출 품질 무시 → 검출 실패가 포즈 실패로 전파.
- [ ] 영상에서 스무딩 없음 → 떨림 심함. One-Euro 필터.
- [ ] mAP만 보고 특정 관절(손목·발목) 약점 방치 → 관절별 OKS 확인.
- [ ] 전신이 필요한데 17키포인트 모델 사용 → DWPose/RTMW로.

---

## 9. 파일명 추천

- **1순위 (영문):** `pose-estimation-openpose-guide.md` *(현재 파일명)*
- 대안:
  - `pose-estimation-rtmpose-vitpose-rtx3060ti.md`
  - `pose-agent-setup.md`
  - 한글 선호 시: `자세추정_OpenPose_가이드.md`

> 세트 구성(비전 스택 5종): `video-qlora-multiagent-guide.md` + `image-classification-transfer-learning-guide.md` + `object-detection-ssd-guide.md` + `semantic-segmentation-pspnet-guide.md` + `pose-estimation-openpose-guide.md`