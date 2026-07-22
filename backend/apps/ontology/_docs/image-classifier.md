# 이미지(화상) 분류 & 전이학습 가이드

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 이미지 분류 모델을 **전이학습(Transfer Learning)** 으로 구축하고, 멀티에이전트 구성요소로 사용
> 짝 문서: `video-qlora-multiagent-guide.md` (동영상 편)
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **이미지 분류는 8GB에서 매우 여유롭다.** 비디오와 달리 Base급(~86–89M) 백본도 **전체 미세조정**이 가능하다.
- **기본 추천 백본:** **DINOv3 ConvNeXt-Tiny/Small** (자연 이미지에서 강력, 가볍고 빠름). 정확도를 더 원하면 **ConvNeXt-Base / ViT-B(DINOv3)**.
- **전이학습의 핵심은 "레짐 선택"이다.** 데이터 양 × 도메인 유사도로 결정: 작고 유사 → **선형 프로브**, 크고/도메인 다름 → **전체 미세조정**.
- **핵심 툴:** **timm**(PyTorch Image Models)이 사실상 표준. + Transformers/PEFT(선택), 증강·MixUp·EMA는 timm 내장.
- **8GB 팁:** bf16(Ampere) + 배치 16~32(224px) + 필요 시 gradient checkpointing. 여기선 QLoRA까지 안 가도 됨.

---

## 1. 8GB VRAM 현실 점검 (이미지 편)

| 작업 | Tiny(~29M) | Base(~86–89M) | Large(~198M) |
|---|---|---|---|
| 추론 | ✅ 대량 처리 | ✅ 여유 | ✅ |
| 선형 프로브(백본 freeze) | ✅ 매우 여유 | ✅ 여유 | ✅ |
| 전체 미세조정(224px) | ✅ | ✅ (배치 16~32) | ⚠️ 배치↓ / grad ckpt |
| 고해상도(384px+) 미세조정 | ✅ | ⚠️ 배치↓ | ⚠️ |

- **동영상과 결정적 차이:** 이미지는 시간축(프레임)이 없어 활성화 메모리가 훨씬 작다. 그래서 3B급 VLM 비디오 학습과 달리 **일반 CNN/ViT 백본은 8GB에서 편하게 학습**된다.
- Ampere라 **bf16 + Flash-Attention 2(ViT계열)** 활용 가능.

---

## 2. 백본 모델 추천

### 2-1. 1순위: DINOv3 (ConvNeXt / ViT)
- **왜:** 자기지도(SSL)로 대규모 학습된 최신 비전 파운데이션 모델. **SigLIP2 등 최신 모델과 이미지 분류에서 대등하거나 우위**, 밀집 예측(세그멘테이션/깊이)에선 격차를 벌린다.
- **timm 지원:** `convnext_tiny.dinov3_lvd1689m`, `convnext_small.*`, `convnext_base.*`, ViT 변형까지 제공(ViT-7B 교사에서 distill).
- **크기 선택(8GB 기준):**
  - **Tiny(~29M) / Small(~50M):** 기본값. 빠르고 정확, 대량 처리·실시간에 유리.
  - **Base(~89M):** 정확도 우선. 전체 미세조정도 8GB 소화.

### 2-2. 대안 백본
| 백본 | 특징 | 언제 |
|---|---|---|
| **DINOv2 (ViT-B/16, ~86M)** | 성숙·안정, 자료 많음 | 안전한 baseline |
| **SigLIP2 / MetaCLIP-2** | 텍스트 정렬 → **zero-shot 분류** 가능 | 라벨 적거나 개방형 분류 |
| **ConvNeXt V2** | 지도학습 CNN 강자 | 순수 분류 정확도·안정 |
| **EVA-02** | 고성능 ViT | 최고 정확도 추구 |
| **ImageNet-21k 지도 사전학습** | 도메인 시프트에 강함 | **X-ray·산업·의료** 등 웹 이미지와 다른 도메인 |

> **도메인 주의:** 자연/RGB 이미지엔 DINOv3가 강하지만, **X-ray·현미경·산업 검사**처럼 웹 이미지와 크게 다른 도메인에선 **ImageNet 지도 사전학습 + 전체 미세조정**이 더 나은 경우가 많다. 도메인이 특수하면 2~3개 백본을 짧게 비교하라.

---

## 3. 전이학습 전략 (이 문서의 핵심)

### 3-1. 4가지 레짐

1. **특징 추출 / 선형 프로브 (Linear Probe)**
   - 백본 **freeze**, 분류 헤드만 학습. VRAM·시간 최소. 특징을 미리 뽑아 캐시하면 CPU로도 학습 가능.
2. **부분 미세조정 (Partial Fine-tune)**
   - 상위 N개 블록만 unfreeze. 선형 프로브와 전체 미세조정의 중간.
3. **전체 미세조정 (Full Fine-tune)**
   - 전 레이어 학습. 데이터 충분/도메인 시프트 클 때 최고 성능. 8GB에서 Base급까지 가능.
4. **LoRA / PEFT (주로 ViT)**
   - 백본은 얼리고 저랭크 어댑터만 학습. **여러 태스크용 어댑터**를 갈아 끼우거나 컴퓨트가 극도로 부족할 때. ConvNeXt(CNN)엔 덜 일반적, ViT엔 잘 맞음.

### 3-2. 어떤 레짐을 쓸까 (데이터 × 도메인 매트릭스)

| | **도메인 유사(자연 이미지)** | **도메인 상이(의료·산업 등)** |
|---|---|---|
| **데이터 적음** | 선형 프로브 (freeze) | 부분 미세조정 + 강한 증강 |
| **데이터 많음** | 부분/전체 미세조정 | 전체 미세조정 (지도 사전학습 고려) |

### 3-3. 실전 스킬

- **레이어별 차등 학습률(discriminative / layer-wise LR decay):** 백본은 낮게(예 1e-5~1e-4), 헤드는 높게(예 1e-3). 하위층일수록 더 작게.
- **점진적 unfreeze:** 헤드만 먼저 몇 에폭 → 상위 블록 순차 해제.
- **스케줄:** warmup + cosine decay. 짧은 warmup이 초반 발산을 막는다.
- **증강:** RandAugment, RandomResizedCrop, HorizontalFlip, Random Erasing. **MixUp / CutMix**는 과적합 억제에 강력(timm 내장).
- **정규화:** label smoothing(0.1), weight decay, dropout, **EMA(가중치 이동평균)**.
- **클래스 불균형:** 가중 손실(class weights), `WeightedRandomSampler`, 또는 focal loss.
- **입력 정규화 일치:** 사전학습 모델의 mean/std·resize를 그대로 써야 함 → timm의 `resolve_model_data_config` 사용(직접 224 하드코딩 금지).
- **평가:** test-time augmentation(TTA), 혼동행렬로 클래스별 약점 파악, early stopping(val 기준).

---

## 4. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 핵심: 이미지 백본 + 학습 유틸의 표준
pip install timm torch torchvision

# HF 생태계(선택): 데이터셋·트레이너·PEFT
pip install transformers datasets accelerate peft

# 실험 추적 / 증강 / 지표
pip install wandb albumentations scikit-learn

# 추론·서빙(선택)
pip install onnx onnxruntime-gpu   # ONNX 내보내기로 경량·고속 추론
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 백본·학습 | **timm** | 사전학습 백본 수백 종 + 증강/MixUp/EMA/train 스크립트 내장 (필수) |
| 데이터·트레이너 | Transformers / datasets / accelerate | HF 파이프라인 선호 시 |
| PEFT | peft | ViT LoRA 어댑터 |
| 증강 | timm / albumentations | RandAugment·CutMix 등 |
| 지표 | scikit-learn | accuracy·F1·혼동행렬 |
| 서빙 | ONNX Runtime / TorchScript | 경량 배포, 에이전트 툴화 |
| 추적 | W&B / TensorBoard | 과적합 모니터 |

---

## 5. 코드 스켈레톤

### 5-1. 전체/부분 미세조정 (timm)

```python
import timm, torch, torch.nn as nn

model = timm.create_model(
    "convnext_small.dinov3_lvd1689m",   # 8GB 기본 추천
    pretrained=True,
    num_classes=NUM_CLASSES,            # 헤드 자동 교체
)

# 입력 전처리는 모델 설정에서 가져오기 (정규화 일치 중요)
cfg = timm.data.resolve_model_data_config(model)
train_tf = timm.data.create_transform(**cfg, is_training=True, auto_augment="rand-m9-mstd0.5")
eval_tf  = timm.data.create_transform(**cfg, is_training=False)

# (선택) 부분 미세조정: 백본 얼리고 마지막 스테이지 + 헤드만 학습
for p in model.parameters():
    p.requires_grad = False
for p in model.get_classifier().parameters():
    p.requires_grad = True
# 상위 블록도 열려면 해당 스테이지 파라미터 requires_grad=True

# 차등 학습률
opt = torch.optim.AdamW([
    {"params": model.get_classifier().parameters(), "lr": 1e-3},
    {"params": [p for n,p in model.named_parameters()
                if p.requires_grad and "head" not in n and "fc" not in n], "lr": 1e-4},
], weight_decay=0.05)

scaler = torch.cuda.amp.GradScaler()
# 학습 루프에서 with torch.autocast("cuda", dtype=torch.bfloat16): ...
```

### 5-2. 선형 프로브 (특징 캐시 → 초저비용)

```python
model = timm.create_model("convnext_tiny.dinov3_lvd1689m",
                          pretrained=True, num_classes=0)  # 특징만
model.eval().cuda()
# 각 이미지의 임베딩을 미리 추출해 저장 → 그 위에 LogisticRegression/선형층만 학습
```

> **timm 내장 `train.py`** 를 쓰면 MixUp·CutMix·EMA·cosine·RandAugment를 플래그만으로 켤 수 있어 실험이 빠르다.

---

## 6. 멀티에이전트 통합

- **이미지 분류 에이전트**로 래핑: 입력=이미지 경로, 출력=`{"label","confidence","topk"}` JSON.
- **동영상 편과 연계:** 비디오에서 키프레임을 뽑아 이 이미지 분류기로 1차 스크리닝 → 애매한 것만 VLM(Qwen-VL)로 에스컬레이션하는 계층 구조도 가능.
- **경량 배포:** ONNX/TorchScript로 내보내 상시 로드. 이미지 분류기는 가벼워 여러 개를 동시에 상주시켜도 8GB에 부담 적음.
- **라우팅:** confidence 임계값 + 클래스별 신뢰도 캘리브레이션(온도 스케일링)으로 오탐 관리.

---

## 7. 함정 체크리스트

- [ ] 사전학습 정규화(mean/std)·입력 크기를 무시하고 임의 224 적용 → 성능 저하. `resolve_model_data_config` 사용.
- [ ] 소량 데이터에서 처음부터 전체 미세조정 → 과적합. 선형 프로브/부분 미세조정부터.
- [ ] 백본과 헤드에 같은 큰 LR 적용 → 사전학습 표현 파괴. **차등 LR** 필수.
- [ ] 도메인 시프트(X-ray 등)인데 DINOv3만 맹신 → ImageNet 지도 사전학습도 비교.
- [ ] 클래스 불균형 방치 → 다수 클래스로 쏠림. 가중 손실/샘플러.
- [ ] Ampere인데 fp32 → bf16으로 속도·메모리 개선.
- [ ] 검증 없이 학습 loss만 보기 → val 기준 early stopping.

---

## 8. 파일명 추천

- **1순위 (영문):** `image-classification-transfer-learning-guide.md` *(현재 파일명)*
- 대안:
  - `image-transfer-learning-rtx3060ti.md`
  - `vision-classifier-agent-setup.md`
  - 한글 선호 시: `화상분류_전이학습_가이드.md`

> 동영상 편(`video-qlora-multiagent-guide.md`)과 세트로 두면 멀티에이전트 문서 묶음이 됩니다.