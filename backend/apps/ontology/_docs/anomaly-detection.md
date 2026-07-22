# GAN 이상 화상 탐지 가이드 — AnoGAN·EGBAD를 넘어서

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 과거 **AnoGAN / Efficient GAN(EGBAD)** 기반 이상 탐지를 최신 방법으로 확장하고, 멀티에이전트 구성요소로 사용
> 짝 문서: 동영상·이미지분류·물체감지·시멘틱분할·자세추정·GAN생성 편
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **솔직한 현실:** 이미지 이상 탐지의 SOTA는 이제 **사전학습 특징 기반 방법**(PatchCore·PaDiM·EfficientAD)이 지배한다. GAN 재구성 기반(AnoGAN/EGBAD)은 **학습 불안정·낮은 정확도**로 대부분 대체됐다.
- **두 갈래로 추천:**
  - **GAN을 계속 쓴다면** → AnoGAN(느림)보다 **EGBAD·f-AnoGAN·GANomaly**(인코더로 빠른 추론), 합성 이상 생성엔 **AnomalyDiffusion/DRAEM**.
  - **정확도가 목적이라면** → **PatchCore**(정확도 최상, MVTec ~99.1% AUROC), **PaDiM**(초고속 프로토타입), **EfficientAD**(밀리초·엣지).
  - **무라벨·신제품 즉시 대응** → **WinCLIP / AnomalyCLIP**(제로샷), **AnomalyGPT**(VLM 설명형).
- **핵심 패러다임:** **원클래스(정상만 학습) / 콜드스타트.** 이상은 드물고 미지라 정상 분포를 모델링하고 이탈을 탐지.
- **8GB 현실:** 대부분 **가볍다.** PatchCore/PaDiM은 경사학습이 사실상 없고, EfficientAD도 경량. GAN 계열도 학습까지 편안.
- **핵심 툴:** **Anomalib**(PatchCore·PaDiM·EfficientAD·FastFlow·DRAEM·GANomaly·WinCLIP 원커맨드).

---

## 1. GAN 이상 탐지 계보 & 패러다임 전환

- **AnoGAN(2017):** 정상 데이터로 GAN 학습 → 테스트 시 **잠재공간을 반복 탐색**해 질의 이미지를 재구성. 이상 점수 = 재구성 오차 + 판별자 특징 잔차. **이미지당 반복 최적화라 느림.**
- **Efficient GAN / EGBAD(2018):** BiGAN/ALI식 **인코더**로 이미지→잠재를 직접 매핑 → AnoGAN의 느린 탐색 제거, **추론 빠름.**
- **f-AnoGAN(2019):** WGAN + 학습된 인코더로 고속화.
- **GANomaly / Skip-GANomaly:** 인코더-디코더-인코더 구조, **잠재 재구성 잔차**로 이상 점수.
- **전환:** 재구성/우도 기반(오토인코더·GAN)은 **PatchCore 등 특징 임베딩 방법**에 자리를 내줬다. 후자는 적대적 학습 없이 **더 정확·안정**하고 학습이 거의 필요 없다.

> **핵심 판단:** "최고 정확도·산업 검사" = 특징 기반(PatchCore/PaDiM/EfficientAD). "GAN 구조 유지·합성 이상 생성" = GAN 계열. "무라벨·신제품 즉시" = 제로샷/VLM. 배타적이지 않고 **하이브리드**가 흔하다.

---

## 2. 8GB VRAM 현실 점검 (이상 탐지 편)

| 방법 | 8GB 학습 | 8GB 추론 | 비고 |
|---|---|---|---|
| **PatchCore** | ✅(특징 추출+메모리뱅크) | ✅ | coreset로 메모리/속도 조절 |
| **PaDiM** | ✅ 초고속(~9초) | ✅ | 프로토타입 최적 |
| **EfficientAD** | ✅ 경량 | ✅ 밀리초 | 엣지·실시간 |
| **FastFlow / RD / STFPM** | ✅ | ✅ | 플로우·학생-교사 |
| **DRAEM** | ✅ | ✅ | 재구성+합성 이상 |
| **AnoGAN/EGBAD/f-AnoGAN/GANomaly** | ✅ | ✅(EGBAD/f는 빠름) | 정확도는 구식 |
| **WinCLIP(제로샷)** | 불필요 | ✅ | CLIP 추론만 |
| **AnomalyGPT(VLM)** | ⚠️ 무거움 | ✅ | 설명형 |

- 이상 탐지는 **정상만 모델링**하므로 대체로 가볍다. PatchCore/PaDiM은 **경사 하강 학습이 사실상 없음**(사전학습 백본 추론 + 통계/메모리뱅크). 8GB에 매우 잘 맞는다.

---

## 3. 모델 추천

### 3-1. 정확도 최상: PatchCore
- 사전학습 백본(WideResNet/DINOv2)에서 **정상 패치 특징을 메모리뱅크**에 저장, **coreset 서브샘플링**(1~25%)으로 압축, 테스트 패치를 **최근접 탐색**해 거리로 이상 점수. **MVTec AD ~99.1% 이미지 AUROC**로 SOTA, 태스크별 학습 불필요.
- **주의:** 이미지 정렬에 민감. coreset 비율로 메모리/정확도 절충.

### 3-2. 초고속 프로토타입: PaDiM
- 패치별 **가우시안 분포** 모델링. PatchCore 대비 **학습 30배 빠름(~9초 vs ~283초)**, 픽셀 AUROC 하락은 미미. **저자원·빠른 반복**에 최적.

### 3-3. 엣지·실시간: EfficientAD
- **학생-교사 지식 증류 + 경량 오토인코더.** 밀리초 지연, **가장 집중된 결함 히트맵.** 실시간 스코어링이 필요한 제약 하드웨어에 적합.

### 3-4. 기타 강력한 특징/재구성 방법
- **FastFlow / CFLOW(정규화 플로우)**: 특징 밀도 추정.
- **Reverse Distillation / STFPM(학생-교사)**: 안정적 로컬라이제이션.
- **DRAEM**: **합성 이상**(Perlin 노이즈 등)으로 판별적 재구성 학습 — 이상 예시 없이도 강함.
- **확산 기반(DiffusionAD 등)**: 다중 클래스 이상 탐지에서 부상.

### 3-5. GAN 트랙 (구조 유지·합성 이상)
- **EGBAD / f-AnoGAN / GANomaly**: 인코더로 빠른 추론. Anomalib에 GANomaly 구현 있음.
- **AnomalyDiffusion**: **소수 샷 이상 이미지 생성** → 지도학습 탐지기 학습 데이터 보강(GAN생성 편과 연결).

### 3-6. 제로샷 / VLM (에이전트 친화)
- **WinCLIP(CVPR 2023):** 정상/이상 텍스트 프롬프트 + 다중 스케일 시각-텍스트 유사도로 **제로/소수 샷** 탐지·분할.
- **AnomalyCLIP(ICLR 2024):** 객체 불문 학습형 프롬프트. **AdaCLIP·VCP-CLIP·PromptAD** 등 변형 다수.
- **AnomalyGPT(AAAI 2024):** LVLM을 이상 탐지·로컬라이제이션·**자연어 설명**에 파인튜닝한 최초 사례. IADGPT·Anomaly-OV 등 후속.
- **트레이드오프:** 제로샷은 신제품에 재학습 없이 대응하나, 정확도는 아직 비지도(PatchCore)에 못 미침. **제로샷 1차 → 필요 시 PatchCore 파인튜닝** 권장.

### 3-7. 비교 요약

| 방법 | 유형 | 8GB | 강점 | 에이전트 적합성 |
|---|---|---|---|---|
| **PatchCore** | 특징 메모리 | ✅ | 정확도 최상 | ★★ |
| **PaDiM** | 특징 통계 | ✅ | 초고속 프로토타입 | ★★ |
| **EfficientAD** | 학생-교사 | ✅ | 밀리초·엣지 | ★★ |
| **DRAEM** | 재구성+합성 | ✅ | 이상 예시 불요 | ★★ |
| **GANomaly/EGBAD** | GAN | ✅ | 구조 유지 | ★ |
| **WinCLIP/AnomalyCLIP** | 제로샷 VLM | ✅ | 무라벨·신제품 | ★★★ |
| **AnomalyGPT** | VLM 설명형 | ⚠️ | 자연어 설명 | ★★★ |

---

## 4. 이상 탐지 핵심 스킬

### 4-1. 원클래스 / 콜드스타트 패러다임
- **정상 이미지만으로 학습.** 학습셋에 이상이 새어들면 성능 붕괴 — 데이터 위생이 최우선.
- 이미지 수준(정상/이상 분류)과 픽셀 수준(로컬라이제이션)을 구분해 설계.

### 4-2. 방법별 핵심 기법
- **PatchCore:** 메모리뱅크 + **coreset 서브샘플링**(속도/메모리 조절), 최근접 탐색.
- **PaDiM:** 패치별 가우시안(평균·공분산).
- **FastFlow:** 특징 위 정규화 플로우 밀도.
- **EfficientAD/STFPM/RD:** 학생-교사 출력 divergence.
- **GAN:** 재구성 오차 + 판별자 특징 잔차(AnoGAN), 잠재 재구성 잔차(GANomaly), 이미지+잠재(EGBAD).

### 4-3. 합성 이상 생성 (지도 신호 만들기)
- **CutPaste, DRAEM(Perlin 노이즈), AnomalyDiffusion**으로 가짜 이상을 만들어 판별력 강화. 실제 이상이 거의 없을 때 유용.

### 4-4. 임계값 설정
- 정상 검증 분포에서 **백분위수/통계 기반**으로 임계값 결정, 또는 소수의 이상 샘플로 **F1-max** 지점 탐색.

### 4-5. 평가 지표
- **Image AUROC**(이미지 수준), **Pixel AUROC**(픽셀), **PRO / AUPRO**(영역 겹침), **F1-max**. 벤치마크: **MVTec AD**, VisA, BTAD, **MVTec LOCO**(논리적 이상), Real-IAD(다시점).

---

## 5. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 핵심: 이상 탐지 SOTA 총망라(원커맨드 학습/추론/벤치마크)
pip install anomalib            # PatchCore·PaDiM·EfficientAD·FastFlow·DRAEM·GANomaly·WinCLIP 등

# 백본(특징 기반)·제로샷
pip install timm open_clip_torch

# 합성 이상 생성(확산)·GAN 커스텀
pip install diffusers transformers   # AnomalyDiffusion 계열
#  PyTorch로 AnoGAN/EGBAD/f-AnoGAN 커스텀 구현

# 배포
pip install onnx onnxruntime-gpu   # Anomalib는 ONNX/OpenVINO 내보내기 지원
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 프레임워크 | **Anomalib** | 대부분 방법 원커맨드, 벤치마크·HPO·엣지 추론 |
| 백본 | timm(WideResNet/DINOv2) | 특징 기반 방법의 인코더 |
| 제로샷 | open_clip | WinCLIP/CLIP 기반 |
| 합성 이상 | Diffusers | AnomalyDiffusion·DRAEM식 |
| GAN 커스텀 | PyTorch | AnoGAN/EGBAD/f-AnoGAN |
| 배포 | ONNX / OpenVINO | 경량·엣지 추론 |

---

## 6. 코드 스켈레톤

### 6-1. PatchCore/EfficientAD (Anomalib, 원커맨드)

```bash
# CLI: 정상만 학습 → 이상 탐지/로컬라이제이션
anomalib train --model Patchcore --data MVTecAD
anomalib train --model EfficientAd --data MVTecAD
anomalib predict --model Patchcore --data MVTecAD --ckpt_path path/to/model.ckpt
```

```python
from anomalib.data import MVTecAD
from anomalib.models import Patchcore, Padim, EfficientAd
from anomalib.engine import Engine

datamodule = MVTecAD(root="datasets/custom", category="my_product")  # 정상 이미지로 구성
model = Patchcore()          # 또는 Padim()(초고속) / EfficientAd()(엣지)
engine = Engine()
engine.fit(model, datamodule=datamodule)     # 정상만 학습
engine.predict(model, datamodule=datamodule) # 이상 점수 + 히트맵
```

### 6-2. GANomaly (Anomalib, GAN 트랙 유지)

```python
from anomalib.models import Ganomaly
model = Ganomaly()           # 인코더-디코더-인코더, 잠재 재구성 잔차
engine.fit(model, datamodule=datamodule)
```

### 6-3. WinCLIP 제로샷 (재학습 없이)

```python
from anomalib.models import WinClip
model = WinClip()            # 정상/이상 텍스트 프롬프트 기반 제로샷
engine.predict(model, datamodule=datamodule)   # 신제품에 즉시 적용
```

---

## 7. 멀티에이전트 통합 (교차 활용이 풍부)

- **이상 탐지 에이전트로 래핑:** 입력=이미지, 출력=`{anomaly_score, is_anomaly, heatmap/mask}` JSON.
- **다른 문서와의 파이프라인:**
  - **검출 → 이상(object-detection 편):** 검출된 객체를 크롭 → **객체별 이상 검사**.
  - **분할 ↔ 이상(segmentation 편):** 이상 히트맵 자체가 픽셀 로컬라이제이션. 마스크로 영역별 판정.
  - **분류(image-classification 편):** 이상이 "이상 있음"을 플래그하면, 알려진 결함 유형은 분류기로 세분.
  - **★ 합성 이상 생성(GAN생성 편):** AnomalyDiffusion으로 가짜 이상/정상을 만들어 탐지기·분류기 학습 보강.
  - **★ VLM 설명(AnomalyGPT식):** 이상 영역을 **자연어로 설명** → 사람이 읽는 검사 리포트.
- **닫힌 루프:** 이상 플래그 → VLM 설명 → 사람 검수 → 피드백 → 재학습.
- **용도:** 산업 품질 검사, 의료 스크리닝, 감시. **콜드스타트**라 이상 라벨 없이 시작 가능.
- **모델 상주:** PatchCore/PaDiM/EfficientAD는 경량이라 상주, VLM은 필요 시 호출(8GB 예산 관리).
- **라우팅:** 이상 점수 임계값 초과 → 상위 에이전트(분류·VLM·사람)로 에스컬레이션.

---

## 8. 함정 체크리스트

- [ ] 학습셋에 이상 이미지 혼입 → 정상 분포 오염. **정상만** 엄격히.
- [ ] PatchCore 정렬 민감성 무시 → 오탐 증가. 촬영 정렬·전처리 일관성.
- [ ] AnoGAN의 이미지당 반복 탐색을 실시간에 사용 → 느림. **EGBAD/f-AnoGAN** 또는 특징 기반으로.
- [ ] 임계값을 임의 고정 → 오탐/미탐 불균형. 정상 검증 분포·F1-max로 설정.
- [ ] Image AUROC만 보고 로컬라이제이션 무시 → **Pixel AUROC·PRO**도 확인.
- [ ] 제로샷으로 미세 결함 정밀 기대 → 정확도는 비지도에 못 미침. 필요 시 PatchCore 파인튜닝.
- [ ] 논리적 이상(배치·개수 오류)을 구조적 방법으로 → **MVTec LOCO**형은 별도 접근.

---

## 9. 파일명 추천

- **1순위 (영문):** `gan-anomaly-detection-guide.md` *(현재 파일명)*
- 대안:
  - `image-anomaly-detection-patchcore-rtx3060ti.md`
  - `anomaly-detection-agent-setup.md`
  - 한글 선호 시: `GAN_이상탐지_가이드.md`

> 세트 구성(비전 스택 7종): `video-qlora-multiagent-guide.md` + `image-classification-transfer-learning-guide.md` + `object-detection-ssd-guide.md` + `semantic-segmentation-pspnet-guide.md` + `pose-estimation-openpose-guide.md` + `gan-image-generation-guide.md` + `gan-anomaly-detection-guide.md`