# 시멘틱 분할 (Semantic Segmentation) 가이드 — PSPNet을 넘어서

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 과거 **PSPNet(Pyramid Scene Parsing Network)** 기반 분할을 최신 모델로 대체하고, 멀티에이전트 구성요소로 사용
> 짝 문서: `video-qlora-multiagent-guide.md`(동영상) · `image-classification-transfer-learning-guide.md`(이미지 분류) · `object-detection-ssd-guide.md`(물체 감지)
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **PSPNet은 피라미드 풀링으로 전역 문맥을 잡은 고전 분할기**다. 현대적 후계자는 **SegFormer**(효율적 트랜스포머)와 **DeepLabV3+**(안정적 CNN)이고, 정확도 최상단은 **Mask2Former**다.
- **8GB 현실:** SegFormer(B0~B2)·DeepLabV3+·smp 계열은 **여유롭게 학습**. **Mask2Former는 학습에 15GB+ 필요**해 8GB에선 추론/소형 설정 위주.
- **추천 3갈래:**
  - 실전 기본값(효율·안정) → **SegFormer** (또는 CNN 베이스라인 **DeepLabV3+**)
  - **프롬프트/영상 추적** → **SAM 2** (점·박스 프롬프트, 프레임 전파, LoRA로 도메인 파인튜닝)
  - **텍스트로 지시(무라벨)** → **Grounded SAM 2 / LangSAM / CLIPSeg** (오픈 보캐블러리 = 에이전트 친화)
- **라벨링 가속:** **SAM 3** 로 오토라벨링 → 지도학습 분할기 학습 데이터 구축.
- **핵심 툴:** Transformers / MMSegmentation / **segmentation-models-pytorch(smp)** + SAM 2·3 + albumentations.

---

## 1. 8GB VRAM 현실 점검 (분할 편)

| 모델/작업 | 8GB 학습 | 8GB 추론 | 비고 |
|---|---|---|---|
| **SegFormer B0~B2** | ✅ | ✅ | 효율·정확 균형, 권장 |
| **DeepLabV3+ (R50/MiT)** | ✅ | ✅ | 안정적 CNN 베이스라인 |
| **smp (U-Net/FPN + encoder)** | ✅ | ✅ | 소량 데이터·의료에 유용 |
| **Mask2Former** | ⚠️ 소형 backbone·작은 crop만 | ✅ | 학습 15GB+ 권장, 8GB엔 빡빡 |
| **SAM 2** | ⚠️ LoRA/디코더만 | ✅ | 프롬프트·영상 전파 |
| **Grounded SAM 2 / LangSAM** | ⚠️ 무거움 | ✅ | 텍스트 제로샷 |

- 분할은 **픽셀 단위 예측 + 고해상도**라 검출·분류보다 **활성화 메모리가 크다.** 8GB에선 **crop 크기·배치**가 핵심 레버.
- Ampere라 **AMP(bf16/fp16) + gradient checkpointing**으로 여유를 만들 수 있다.

---

## 2. 모델 추천

### 2-1. 실전 기본값: SegFormer (또는 DeepLabV3+)
- **SegFormer:** 계층형 트랜스포머 인코더(MiT-B0~B5) + 가벼운 MLP 디코더. **효율 대비 정확도가 뛰어나고** 여러 도메인에서 안정적이라 8GB의 실용적 기본값.
- **DeepLabV3+:** ASPP(atrous) 기반 CNN. **검증된 안정성과 광범위한 프레임워크 지원.** PSPNet과 같은 계보의 든든한 대안.
- **PSPNet 대체 관점:** 두 모델 모두 전역 문맥 모델링을 현대적으로 개선 → 정확도·효율 향상. 기존 파이프라인을 그대로 옮기기 쉬움.
- **크기 선택(8GB):** 프로토타입 **B0/B1**, 정확도 필요 시 **B2**.

### 2-2. 정확도 최상단: Mask2Former (조건부)
- **마스크 분류 + 마스크드 어텐션**으로 시맨틱/인스턴스/파놉틱을 **통합**. 최고 정확도.
- **주의:** 학습에 **최소 15GB, Swin-L은 32GB+** 필요. 8GB에선 **소형 backbone·작은 crop·추론 위주**로만 현실적. 정확도가 꼭 필요하면 클라우드 GPU에서 학습 후 로컬 추론.

### 2-3. 프롬프트/영상: SAM 2
- **점·박스 프롬프트로 무엇이든 분할**, **메모리로 프레임 간 객체 추적** → 이미지·영상 통합.
- **도메인 파인튜닝:** 이미지 인코더+마스크 디코더 튜닝, 또는 **LoRA(SAMed 방식)·어댑터**로 소량 데이터에서도 SOTA급 성능 사례 다수(의료 등).
- **에이전트 관점:** 검출기가 준 박스를 프롬프트로 넣어 **정밀 마스크**를 얻는 조합이 강력.

### 2-4. 텍스트 제로샷 (에이전트 친화): Grounded SAM 2 / LangSAM / CLIPSeg
- **텍스트 프롬프트로 분할** — 라벨 없이 "빨간 헬멧", "물웅덩이"를 마스크로. Grounded SAM 2는 그라운딩 검출 + SAM 2 결합.
- **트레이드오프:** 미세 경계 정밀도는 지도학습 모델보다 낮고 연산이 무겁다. **텍스트로 1차 → 필요 시 전용 모델 파인튜닝**을 권장.

### 2-5. 라벨링 가속: SAM 3
- **오픈 보캐블러리 오토라벨링**에 특히 유용. 추론 배포보다 **데이터 라벨링 워크플로**에서 진가를 발휘(경계 안정성 우수, 다만 실시간 검출기보다 느림).
- 활용: SAM 3로 마스크 초안 생성 → 사람 검수 → SegFormer/DeepLab 학습 데이터로.

### 2-6. 도메인 특화
- **의료 영상:** **nnU-Net**(자동 구성, 이 영역에선 트랜스포머가 CNN을 못 넘는 경우 많음), 또는 U-Net(smp).
- **실시간/엣지:** YOLO-seg 계열(인스턴스), STDC 등 경량 모델.

### 2-7. 비교 요약

| 모델 | 유형 | 8GB 학습 | 강점 | 에이전트 적합성 |
|---|---|---|---|---|
| **SegFormer** | 지도 트랜스포머 | ✅ | 효율·정확 균형 | ★★ |
| **DeepLabV3+** | 지도 CNN | ✅ | 안정·호환 | ★★ |
| **Mask2Former** | 통합 트랜스포머 | ⚠️ | 최고 정확도 | ★★ |
| **SAM 2** | 프롬프트/영상 | ⚠️ LoRA | 프롬프트·추적 | ★★★ |
| **Grounded SAM 2 / LangSAM** | 오픈보캐블러리 | ⚠️ | 텍스트·무라벨 | ★★★ |
| nnU-Net / U-Net | 지도 CNN | ✅ | 의료·소량 데이터 | ★ |

---

## 3. 손실함수 · 전이학습 · 데이터 전략

### 3-1. 손실함수 스킬 (분할의 핵심)
- **Cross-Entropy(CE):** 기본. `ignore_index`로 미라벨 픽셀 제외.
- **Dice / Tversky:** 영역 겹침 최적화, **클래스 불균형·소형 영역**에 강함.
- **Focal:** 어려운 픽셀 가중.
- **Lovász-Softmax:** mIoU 직접 최적화.
- **조합 권장:** `CE + Dice` 가 실무 기본 조합. 불균형 심하면 `Focal + Dice`.
- **OHEM(online hard example mining):** 어려운 픽셀만 역전파.

### 3-2. 전이학습
- **ImageNet/ADE20K/Cityscapes 사전학습 backbone**에서 출발. 데이터 적으면 **backbone freeze → 디코더만 학습** 후 점진적 unfreeze.
- **차등 학습률:** backbone 낮게, 디코더/헤드 높게.
- SAM 계열은 **LoRA/어댑터**로 소량 도메인 데이터에 효율적 적응.

### 3-3. 데이터·증강
- **라벨 형식:** 클래스 인덱스 **PNG 라벨맵**(팔레트 주의), COCO-stuff/ADE20K/Cityscapes 포맷.
- **주석 도구:** CVAT, Label Studio, Roboflow, **SAM 보조 라벨링**(클릭→마스크).
- **증강(albumentations):** RandomScale, RandomCrop, Flip, ColorJitter. **마스크는 최근접(nearest) 보간**으로 리샘플. Copy-Paste/CutMix는 마스크 동기화 주의.

### 3-4. 해상도·추론 스킬
- **crop 크기 ↔ 메모리** 트레이드오프: 8GB는 보통 **512×512 crop**부터.
- **대형 이미지:** **슬라이딩 윈도우 추론**으로 타일 처리 후 병합.
- **후처리:** (고전) CRF, 경계 refinement, **TTA(멀티스케일/플립)** 로 mIoU 소폭 향상.

### 3-5. 평가 지표
- **mIoU(주지표)**, 클래스별 IoU, 픽셀 정확도, **Boundary F1**(경계 품질). 검증 mIoU 기준 early stopping.

---

## 4. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 트랜스포머 분할 (SegFormer, Mask2Former, OneFormer, DPT 등)
pip install transformers datasets accelerate

# 쉬운 U-Net/DeepLab/FPN + 수십 종 encoder
pip install segmentation-models-pytorch

# 증강 (분할 마스크 동기화)
pip install albumentations

# 지표·후처리·시각화
pip install scikit-learn supervision

# 배포
pip install onnx onnxruntime-gpu

# SAM 2 / SAM 3 (프롬프트·오픈보캐블러리) — 공식 리포에서 설치
#  pip install "git+https://github.com/facebookresearch/sam2.git"

# (선택) 종합 프레임워크: PSPNet·DeepLab·SegFormer·Mask2Former 총망라
#  pip install mmengine mmcv mmsegmentation   # 설정 복잡, 필요 시만
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 트랜스포머 분할 | **Transformers** | SegFormer·Mask2Former·OneFormer 즉시 사용 |
| 쉬운 학습 | **segmentation-models-pytorch(smp)** | U-Net/DeepLab + encoder 조합, 8GB 친화 |
| 종합 | MMSegmentation | PSPNet 포함 전 모델·backbone(무겁지만 강력) |
| 프롬프트/영상 | **SAM 2 / SAM 3** | 프롬프트 분할·영상 전파·오토라벨링 |
| 증강 | albumentations | 이미지-마스크 동기 증강 |
| 배포 | ONNX Runtime / TensorRT | 경량·고속 추론, 에이전트 툴화 |

---

## 5. 코드 스켈레톤

### 5-1. SegFormer 파인튜닝 (Transformers)

```python
from transformers import SegformerForSemanticSegmentation, SegformerImageProcessor
import torch

proc = SegformerImageProcessor(do_reduce_labels=False)
model = SegformerForSemanticSegmentation.from_pretrained(
    "nvidia/segformer-b1-finetuned-ade-512-512",   # 사전학습에서 출발
    num_labels=NUM_CLASSES, ignore_mismatched_sizes=True,   # 헤드 교체
)

# 학습 루프: AMP + 작은 배치 + (필요시) gradient checkpointing
model.gradient_checkpointing_enable()
# with torch.autocast("cuda", dtype=torch.bfloat16): outputs = model(pixel_values, labels=labels)
# loss = outputs.loss  (내부 CE). 불균형이면 커스텀 CE+Dice 사용
```

### 5-2. smp로 U-Net/DeepLab (소량 데이터·의료)

```python
import segmentation_models_pytorch as smp

model = smp.Unet(                     # 또는 smp.DeepLabV3Plus
    encoder_name="tu-convnext_small.dinov3_lvd1689m",  # timm encoder 사용 가능
    encoder_weights="imagenet",
    in_channels=3, classes=NUM_CLASSES,
)
loss = smp.losses.DiceLoss(mode="multiclass") + torch.nn.CrossEntropyLoss()  # 개념적 조합
```

### 5-3. SAM 2 프롬프트 분할 (검출 박스 → 정밀 마스크)

```python
from sam2.sam2_image_predictor import SAM2ImagePredictor
predictor = SAM2ImagePredictor.from_pretrained("facebook/sam2-hiera-small")
predictor.set_image(image)
masks, scores, _ = predictor.predict(box=detected_bbox)  # 검출기 bbox를 프롬프트로
```

---

## 6. 멀티에이전트 통합

- **분할 에이전트로 래핑:** 입력=이미지(+선택 프롬프트), 출력=라벨맵 또는 객체별 마스크(RLE/polygon) JSON.
- **프롬프트 수용:** SAM 2에 점/박스, LangSAM/CLIPSeg에 텍스트를 넘겨 재학습 없이 대상 분할.
- **4문서 파이프라인 완성:**
  - **검출 → 분할:** `object-detection` 에이전트의 bbox → SAM 2 박스 프롬프트 → **정밀 마스크**.
  - **분할 → 분류:** 마스크로 영역 크롭 → `image-classification` 에이전트로 세부 라벨.
  - **영상:** `video` 편과 연계, SAM 2 **마스크 프레임 전파**로 객체 추적.
  - **데이터 생성:** SAM 3 오토라벨링 → SegFormer 학습셋 구축.
- **경량 배포:** SegFormer-B0/DeepLab을 ONNX/TensorRT로 상시 로드, SAM 계열은 필요 시 호출로 VRAM 절약.
- **라우팅:** 픽셀 신뢰도/경계 품질이 낮으면 상위 에이전트(전용 모델·사람 검수)로 에스컬레이션.

---

## 7. 함정 체크리스트

- [ ] 라벨맵 팔레트/인덱스 혼동 → 학습 실패. 클래스 인덱스와 `ignore_index` 확인.
- [ ] 마스크를 이중선형 보간으로 리샘플 → 라벨 오염. **최근접 보간** 사용.
- [ ] 클래스 불균형에 CE만 사용 → 소수 클래스 무시. **CE+Dice/Focal**.
- [ ] 8GB에 Mask2Former 전체 학습 시도 → OOM. SegFormer/smp로 대체하거나 클라우드 학습.
- [ ] crop만 키우다 OOM → AMP·gradient checkpointing·배치 조정.
- [ ] mIoU만 보고 경계 품질 무시 → **Boundary F1**도 확인.
- [ ] 오픈보캐블러리로 미세 경계 정밀 기대 → 좁은 도메인은 지도 파인튜닝 필요.

---

## 8. 파일명 추천

- **1순위 (영문):** `semantic-segmentation-pspnet-guide.md` *(현재 파일명)*
- 대안:
  - `semantic-segmentation-segformer-sam2-rtx3060ti.md`
  - `segmentation-agent-setup.md`
  - 한글 선호 시: `시멘틱분할_PSPNet_가이드.md`

> 세트 구성(비전 스택 4종): `video-qlora-multiagent-guide.md` + `image-classification-transfer-learning-guide.md` + `object-detection-ssd-guide.md` + `semantic-segmentation-pspnet-guide.md`