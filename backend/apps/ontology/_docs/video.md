# 동영상 분류 3DCNN 대체용 QLoRA 모델 & 멀티에이전트 구축 가이드

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: 과거 동영상 분류용 **3DCNN**을 대체하는 모델을 **QLoRA**로 파인튜닝하고, 멀티에이전트 구성요소로 사용
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **8GB VRAM에서 비디오 VLM을 "학습"까지 하는 건 빡빡하다.** 추론은 여유롭지만, 파인튜닝은 프레임 수·해상도·배치를 강하게 줄여야 돌아간다.
- **추천 조합은 "하이브리드"다.**
  - 무거운 추론/에이전트 두뇌 → **Qwen2.5-VL-3B-Instruct** (QLoRA 대상, 비디오 네이티브, 자연어·JSON 출력 → 에이전트 친화)
  - 순수 분류(3DCNN 직접 대체) → **VideoMAE-base** (86M급, 8GB에서 편하게 학습·추론, 처리량 높음)
- **핵심 툴체인:** Unsloth + Transformers + PEFT + bitsandbytes(4-bit NF4) + TRL, 추론은 GGUF(Ollama/llama.cpp) 또는 vLLM, 오케스트레이션은 LangGraph/CrewAI.
- **8GB 생존 기법:** 4-bit NF4 + double quant + paged optimizer, gradient checkpointing/accumulation, 프레임 4~8장·저해상도, 비전 인코더 freeze, LoRA rank 8~16.

---

## 1. 8GB VRAM 현실 점검

| 작업 | 3B급 비디오 VLM | VideoMAE-base(86M) |
|---|---|---|
| 4-bit 추론 | ✅ 여유 (가중치 ~2GB) | ✅ 매우 여유 |
| LoRA/QLoRA 학습 | ⚠️ 가능하나 빡빡 (프레임·해상도 강제 축소 필요) | ✅ 편함 (헤드/전체 미세조정도 가능) |
| 풀 파인튜닝 | ❌ 불가 (다중 GPU/24GB+ 필요) | ⚠️ 프레임 줄이면 부분 가능 |

- **RTX 3060 Ti = Ampere**이라 `bf16`, `bitsandbytes 4-bit`, `Flash-Attention 2`를 모두 쓸 수 있다. 이게 8GB에서 큰 이점.
- 비디오는 이미지보다 **비주얼 토큰이 프레임 수만큼 배로 늘어난다.** VLM 학습 시 OOM의 주범은 가중치가 아니라 **활성화(activation) 메모리**다. → 프레임 수와 해상도가 VRAM을 지배한다.

---

## 2. 모델 추천

### 2-1. 1순위 (QLoRA + 에이전트): Qwen2.5-VL-3B-Instruct
- **왜:** 비디오를 네이티브로 입력받고, 결과를 **자연어/구조화 JSON**으로 낸다. 즉 "라벨만 뱉는 분류기"가 아니라 멀티에이전트에서 **추론·라우팅·근거 설명**까지 가능.
- **VRAM:** 4-bit 추론 시 가중치 ~2GB. QLoRA 학습은 프레임 4~8 / 저해상도로 제한하면 8GB에 진입 가능.
- **최신 대안:** **Qwen3-VL-2B / 4B**, **Qwen3.5-VL** 계열도 나와 있음. 2B가 8GB 학습엔 더 안전. 더 좋은 품질을 원하면 4B를 추론 전용으로.

### 2-2. 3DCNN 직접 대체(순수 분류): VideoMAE-base
- **왜:** 트랜스포머 기반 비디오 분류의 표준. 3DCNN(I3D, R(2+1)D, SlowFast 등) 대비 **정확도·전이학습 효율**이 좋고, HF `transformers`에 분류 파이프라인이 그대로 있다.
- **체크포인트:** `MCG-NJU/videomae-base` 또는 `MCG-NJU/videomae-base-finetuned-kinetics` (도메인 겹치면 후자가 유리).
- **8GB 적합성:** 86M급이라 QLoRA가 필요 없을 정도. LoRA(PEFT) 또는 헤드/전체 미세조정 모두 8GB에서 소화.
- **경쟁 모델:** TimeSformer(divided space-time attention, 미세동작에 강함), Video Swin, ViViT, V-JEPA. 정확도 벤치마크상 도메인마다 우열이 갈리니 2~3개를 짧게 비교해보는 걸 권장.

### 2-3. 비교 요약

| 모델 | 파라미터 | 8GB 학습 | 출력 형태 | 3DCNN 대체 적합성 | 에이전트 적합성 |
|---|---|---|---|---|---|
| **Qwen2.5-VL-3B** | ~3.8B | ⚠️ 조건부 | 자연어/JSON | 상 (추론형 분류) | ★★★ |
| **Qwen3-VL-2B** | ~2B | ✅ | 자연어/JSON | 상 | ★★★ |
| **VideoMAE-base** | ~86M | ✅ | 클래스 로짓 | ★★★ (직접 대체) | ★ (툴로 래핑) |
| TimeSformer | ~121M | ✅ | 클래스 로짓 | ★★★ | ★ |

> **의사결정 가이드**
> - "라벨만 정확히" + 처리량 중요 → **VideoMAE / TimeSformer**
> - "라벨 + 근거 설명 + 다른 에이전트와 대화" → **Qwen-VL 계열**
> - 둘 다 필요 → **아래 하이브리드 아키텍처**

---

## 3. 멀티에이전트 아키텍처 제안 (하이브리드)

```
                 ┌─────────────────────────┐
   사용자/이벤트 →│   Orchestrator (LangGraph) │
                 └───────────┬─────────────┘
                             │ 라우팅
          ┌──────────────────┼───────────────────┐
          ▼                  ▼                   ▼
 ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
 │ 분류 에이전트    │  │ 추론/판단 에이전트 │  │ 후처리 에이전트   │
 │ VideoMAE (tool) │  │ Qwen2.5-VL-3B   │  │ (LLM/규칙)      │
 │ 빠른 1차 라벨    │→ │ 근거·경계 케이스  │→ │ 액션·요약·기록    │
 └────────────────┘  └────────────────┘  └────────────────┘
```

- **1차 분류(빠름):** VideoMAE가 저비용으로 대량 클립을 라벨링 → 3DCNN이 하던 일을 그대로 대체.
- **2차 판단(정확·설명):** 애매하거나 confidence 낮은 클립만 Qwen-VL로 넘겨 자연어 근거 + 재분류.
- **장점:** 8GB에서 VLM을 항상 돌릴 필요 없이 **"필터 → 정밀"** 2단으로 나눠 비용·메모리 절약. VideoMAE는 상시 로드, Qwen-VL은 필요 시만 호출.

---

## 4. 최적화된 툴체인 (설치 & 역할)

```bash
# 1) 파이썬 환경
python -m venv venv && source venv/bin/activate
pip install -U pip

# 2) 학습 스택 (QLoRA)
pip install unsloth                      # 2~5x 빠르고 VRAM 50~70% 절감 (8GB 필수템)
pip install transformers accelerate peft bitsandbytes trl
pip install "qwen-vl-utils[decord]"      # Qwen-VL 비디오/이미지 전처리
pip install flash-attn --no-build-isolation   # Ampere 지원, 활성화 메모리 절감

# 3) 비디오 처리 (VideoMAE 경로)
pip install pytorchvideo decord av opencv-python

# 4) 추론/서빙
pip install vllm                         # GPU 서빙 (양자화 지원)
#  또는 GGUF 변환 후 Ollama/llama.cpp 로 경량 서빙

# 5) 멀티에이전트 오케스트레이션
pip install langgraph                     # 상태 기반 에이전트 그래프 (권장)
#  대안: crewai, autogen

# 6) 실험 추적
pip install wandb                         # 또는 tensorboard
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 학습 가속 | **Unsloth** | 8GB QLoRA의 핵심. 커널 최적화로 VRAM/시간 절감, 비전 파인튜닝 지원 |
| 표준 학습 | Transformers + PEFT + bitsandbytes | 4-bit NF4 QLoRA 정석 스택 |
| 트레이너 | TRL `SFTTrainer` | 학습 루프·데이터 콜레이터 |
| 비디오 전처리 | qwen-vl-utils / PyTorchVideo / decord | 프레임 샘플링·정규화 |
| 메모리 | Flash-Attention 2, gradient checkpointing | 활성화 메모리 절감 |
| 서빙 | vLLM / GGUF(Ollama) | 양자화 추론 |
| 오케스트레이션 | LangGraph / CrewAI | 에이전트 라우팅·툴 호출 |
| 추적 | W&B / TensorBoard | loss·과적합 모니터링 |

---

## 5. QLoRA 파인튜닝 스킬 (8GB 생존 전략)

우선순위 순서로 적용. 위에서부터 VRAM 절감 효과가 크다.

1. **4-bit NF4 로드 + double quantization**
   - `BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type="nf4", bnb_4bit_use_double_quant=True, bnb_4bit_compute_dtype=torch.bfloat16)`
2. **프레임 수·해상도 축소 (비디오 최대 레버)**
   - 프레임: **4~8장**으로 uniform sampling. 16장부터는 8GB에서 위험.
   - 해상도: Qwen-VL은 `min_pixels`/`max_pixels`로 비주얼 토큰 수를 직접 제어 → 낮게 잡기.
3. **비전 인코더 freeze, 언어층에만 LoRA**
   - Unsloth에서 vision/language/attention/MLP 중 학습 대상 선택 가능. 언어층 위주로.
4. **gradient checkpointing** (`use_gradient_checkpointing="unsloth"`) — 활성화 재계산으로 메모리↓
5. **batch_size=1 + gradient_accumulation** (예: accum 8 → 유효 배치 8)
6. **paged 8-bit optimizer** (`optim="paged_adamw_8bit"`) — 옵티마이저 상태 페이징
7. **LoRA 설정**: `r=8~16`, `alpha=16~32`, `dropout=0.05`, target = `q_proj,k_proj,v_proj,o_proj` (+ MLP는 여유 있을 때)
8. **max_seq_length 축소** — 비주얼 토큰 포함이라 짧게.
9. 그래도 OOM이면: 프레임 수↓ → 해상도↓ → LoRA rank↓ 순으로 후퇴.

> **VideoMAE 경로**는 위 QLoRA가 과할 수 있음. 86M급이라 **PEFT-LoRA 또는 헤드 파인튜닝**으로 충분하고, `per_device_train_batch_size` 2~4까지 여유. `UniformTemporalSubsample`로 프레임 16장, 224px면 8GB 안에서 학습 가능.

---

## 6. 데이터 준비 스킬

- **VideoMAE (분류):** `(video_clip, label)` 형태. 프레임 균일 샘플링 → 정규화 → 랜덤 크롭/플립 증강. 클래스 불균형 시 `WeightedRandomSampler`.
- **Qwen-VL (지시형):** 대화(ChatML) 포맷. 예:
  ```json
  {"messages":[
    {"role":"user","content":[
      {"type":"video","video":"clip_001.mp4","max_pixels":50176},
      {"type":"text","text":"이 영상의 행동을 다음 라벨 중 하나로 분류하고 근거를 JSON으로 답하라: [A,B,C]"}]},
    {"role":"assistant","content":"{\"label\":\"A\",\"reason\":\"...\"}"}
  ]}
  ```
- **품질이 성패를 좌우**한다. 파일 경로·라벨·주석 불일치는 "학습은 되는데 아무것도 안 배우는" 조용한 실패를 만든다. 500~2,000개의 잘 정제된 예시가 대량의 지저분한 데이터보다 낫다.
- 지식 주입은 파인튜닝보다 **RAG/프롬프트**로, 포맷 고정은 **structured output**으로 먼저 시도하고, 그래도 안 되는 "스타일·도메인 어휘·툴콜 스키마" 때만 파인튜닝.

---

## 7. 학습 코드 스켈레톤 (Unsloth + Qwen-VL, QLoRA)

```python
from unsloth import FastVisionModel
import torch

model, processor = FastVisionModel.from_pretrained(
    "unsloth/Qwen2.5-VL-3B-Instruct",   # 또는 Qwen3-VL-2B 계열
    load_in_4bit=True,
    use_gradient_checkpointing="unsloth",
)

model = FastVisionModel.get_peft_model(
    model,
    finetune_vision_layers=False,   # 비전 인코더 freeze (VRAM 절감)
    finetune_language_layers=True,
    finetune_attention_modules=True,
    finetune_mlp_modules=True,
    r=8, lora_alpha=16, lora_dropout=0.05, bias="none",
)

# ... dataset 준비(대화 포맷) ...

from trl import SFTTrainer, SFTConfig
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=SFTConfig(
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        num_train_epochs=3,
        learning_rate=2e-4,
        bf16=True,
        optim="paged_adamw_8bit",
        max_seq_length=2048,
        logging_steps=5,
        output_dir="outputs",
    ),
)
trainer.train()
```

> 학습 중 **validation loss가 다시 오르면 즉시 early stop**. 3B 비디오 파인튜닝은 과적합이 빠르다.

---

## 8. 추론·서빙 최적화

- **경량 서빙:** LoRA 어댑터 merge → **GGUF Q4 변환 → Ollama/llama.cpp**. 8GB에서 가장 안정적.
- **GPU 서빙:** vLLM (4-bit/AWQ). 비디오는 `--limit-mm-per-prompt`로 프레임 상한, `--max-model-len` 축소로 KV 캐시 절감.
- 상시 로드는 **VideoMAE만**, Qwen-VL은 요청 시 로드/언로드하여 8GB를 아낀다.

---

## 9. 에이전트 통합 스킬

- 모델을 **툴(tool)로 래핑**: 입력=클립 경로, 출력=`{"label","confidence","reason"}` JSON. LangGraph 노드에서 호출.
- **구조화 출력 강제**: 프롬프트에 JSON 스키마 명시 + 파싱 실패 시 재시도 노드.
- **라우팅 규칙**: VideoMAE confidence ≥ 임계값이면 확정, 미만이면 Qwen-VL 에스컬레이션 → 비용/지연 최소화.
- **관측성**: 각 에이전트 호출을 W&B/로그로 남겨 라벨 드리프트 추적.

---

## 10. 함정 체크리스트

- [ ] 프레임 16장으로 시작 → 십중팔구 OOM. **4~8장부터** 올려가기.
- [ ] Qwen3-VL/Qwen3.5는 `transformers` 최신(v5+) 필요. 버전 안 맞으면 로드 실패.
- [ ] 지식·사실을 파인튜닝으로 주입하려다 실패 → RAG로.
- [ ] 데이터 경로/라벨 불일치로 "조용한 학습 실패".
- [ ] 8GB에서 풀 파인튜닝 시도 금지(다중 GPU/24GB+).
- [ ] bf16 미사용(Ampere인데 fp32) → 불필요한 VRAM 낭비.

---

## 11. 파일명 추천

- **1순위 (영문, git/파일시스템 안전):** `video-qlora-multiagent-guide.md` *(현재 파일명)*
- 대안:
  - `3dcnn-to-vlm-migration-rtx3060ti.md`
  - `video-classification-agent-setup.md`
  - 한글 선호 시: `동영상분류_QLoRA_멀티에이전트_구축가이드.md`

> 협업/버전관리를 생각하면 **영문·하이픈 케이스**를 권장합니다.