# 자연어 처리 감정 분석 가이드 — Transformer 기반

> 대상 하드웨어: **RTX 3060 Ti (VRAM 8GB, Ampere sm_86) / RAM 32GB**
> 목표: **Transformer 기반 감정/감성 분석**을 구축하고, 멀티에이전트의 **NLP·언어 컴포넌트**로 사용
> 짝 문서: 비전 스택 7종(동영상·이미지분류·물체감지·시멘틱분할·자세추정·GAN생성·이상탐지)
> 작성일 기준: 2026-07

---

## 0. 30초 요약 (TL;DR)

- **핵심 판단(2026):** 감정 분류 같은 **"이해·분류" 태스크는 인코더 파인튜닝(BERT/ModernBERT)이 LLM보다 빠르고 싸고 종종 더 정확하다.** (NIST: 특화 모델이 범용 대비 도메인 태스크에서 23~37% 우위.) LLM은 **제로샷·설명·미묘한 케이스**에서 빛난다.
- **모델 추천:**
  - 영어/다국어 인코더 → **ModernBERT**(8K 컨텍스트, 2~4배 빠름) / **DeBERTa-v3 / RoBERTa / XLM-RoBERTa**(다국어)
  - **한국어** → **KcELECTRA**(댓글·리뷰 등 노이즈 텍스트) / **KLUE-RoBERTa**(표준 문어) / **KoELECTRA**
  - 라벨 적음 → **SetFit**(소수 샷), 라벨 없음 → **제로샷(NLI/LLM)**
  - 설명·ABSA·추론 → 소형 LLM **QLoRA**(Qwen/Llama/Gemma)
- **8GB 현실:** 인코더(110~395M) 파인튜닝은 **매우 여유**. LLM은 QLoRA로 가능. 이 시리즈에서 가장 가벼운 축.
- **멀티에이전트:** **인코더 1차(빠름) + LLM 2차(설명·경계 케이스)** 하이브리드. 비전 스택과 **멀티모달 감성**으로 연결 가능.

---

## 1. 인코더 vs LLM — 2026년의 정직한 정리

| 기준 | 인코더 파인튜닝 | LLM(생성형) |
|---|---|---|
| 정확도(분류) | ★★★ (도메인 데이터 있으면 최상) | ★★ (프롬프트/파인튜닝 의존) |
| 속도·비용 | ★★★ (수 ms, 저렴) | ★ (느리고 비쌈) |
| 라벨 없음(제로샷) | △ (NLI 트릭 필요) | ★★★ |
| 설명·추론·ABSA | △ | ★★★ (자연어 근거) |
| 8GB 학습 | ★★★ | ★★ (QLoRA) |

- **결론:** 프로덕션 감정 분류의 **실전 기본은 인코더 파인튜닝.** 제로샷·설명·미묘한 표적 감성은 LLM. 연구에 따르면 **적당히 파인튜닝한 중형 인코더가 fine-grained 태스크에서 in-context LLM을 앞서기도** 하고, 반대로 **좋은 프롬프트의 LLM이 ABSA에서 SOTA에 근접**하기도 한다 → 태스크·데이터로 판단.

---

## 2. 8GB VRAM 현실 점검 (NLP 편)

| 방법 | 8GB 학습 | 비고 |
|---|---|---|
| 인코더 base(110~340M) | ✅ 매우 여유 | 배치 16~32, 짧은 학습 |
| ModernBERT-large(395M) | ✅ | AMP·batch 조정 |
| SetFit(소수 샷) | ✅ 초경량 | 수십~수백 예시 |
| 제로샷 NLI 추론 | 학습 불필요 | BART/DeBERTa-MNLI |
| LLM QLoRA(1~8B) | ✅(Unsloth) | 4bit + 배치 1 |

- 텍스트 분류는 이미지·비디오 대비 **활성화 메모리가 작다.** 8GB에서 인코더 파인튜닝은 **분 단위**로 끝나는 경우가 많다.

---

## 3. 모델 추천

### 3-1. 영어/다국어 인코더
- **ModernBERT(2024, Answer.AI/LightOn):** 인코더 전용, **8,192 토큰** 컨텍스트, RoPE·교대 global/local 어텐션·GeGLU·Flash Attention·unpadding, 2조 토큰 학습. 이전 인코더 대비 **2~4배 빠르고** 분류·검색에서 SOTA. **2026 기본값.** (large 395M)
- **DeBERTa-v3 / RoBERTa:** 여전히 강력한 분류 백본.
- **XLM-RoBERTa:** 다국어·코드스위칭.

### 3-2. 한국어 인코더 (사용자 우선 고려)
- **KcELECTRA / KcBERT(Beomi):** **뉴스 댓글·대댓글 등 사용자 생성·노이즈 텍스트**로 학습 → 리뷰·SNS·댓글 감성에 강함. KcELECTRA가 데이터·vocab 확장으로 KcBERT 대비 향상.
- **KLUE-RoBERTa / KLUE-BERT:** KLUE 벤치마크 기반, **표준 문어** 이해 우수.
- **KoELECTRA:** 일반 코퍼스 → 보편 태스크에 유리. **KoBERT(SKT):** 고전 한국어 BERT.
- **선택 가이드:** 댓글·리뷰·구어체 → **KcELECTRA**; 뉴스·공식 문서 → **KLUE-RoBERTa/KoELECTRA**.
- **데이터:** AI Hub 한국어 감정 데이터셋(긍/부/중립 또는 기쁨·분노·슬픔·불안·당황·상처 등 6~7분류, 9분류 변형).

### 3-3. 라벨이 적거나 없을 때
- **SetFit(소수 샷):** 문장 임베딩 대조학습 → **수십~수백 예시**로 강한 분류기. 프롬프트 불필요, 초경량.
- **제로샷 NLI:** `BART-large-MNLI`, `DeBERTa-MNLI`, 다국어 `XLM-R-XNLI`로 라벨을 가설로 넣어 분류.
- **LLM 제로/소수 샷:** 지시형 프롬프트 + in-context 예시.

### 3-4. LLM 트랙 (설명·ABSA·추론)
- 소형 LLM(**Qwen/Llama/Gemma 1~8B**)을 **QLoRA**로 파인튜닝하거나 프롬프트로. **표적 감성·측면 기반·자연어 근거**가 필요할 때. 금융 뉴스 등에서 7B급 LLM이 특화 모델을 능가한 사례도 있음.

### 3-5. 비교 요약

| 모델 | 유형 | 8GB | 강점 |
|---|---|---|---|
| ModernBERT | 인코더 | ✅ | 빠름·긴 문맥·분류 SOTA |
| DeBERTa-v3/RoBERTa | 인코더 | ✅ | 안정적 고성능 |
| KcELECTRA | 인코더(한) | ✅ | 댓글·리뷰 노이즈 텍스트 |
| KLUE-RoBERTa | 인코더(한) | ✅ | 표준 한국어 |
| SetFit | 임베딩 소수샷 | ✅ | 라벨 극소량 |
| LLM(QLoRA) | 생성형 | ✅ | 제로샷·설명·ABSA |

---

## 4. 태스크 유형별 접근

- **문서/문장 극성(polarity):** 긍정/부정/중립 다중 클래스(softmax + CrossEntropy).
- **측면 기반 감성(ABSA):** `문장 [SEP] 측면어` 입력으로 교차 어텐션 유도 → 측면별 감성. (ModernBERT-large ABSA가 좋은 사례.)
- **감정 분류(emotion):** 다중 클래스(기쁨/분노/슬픔…) 또는 **다중 라벨**(한 문장에 여러 감정) → **sigmoid + BCE**. GoEmotions(27), Ekman(6), 한국어 6~9분류.
- **감성 강도(intensity):** 회귀(MSE) 또는 순서형 분류.
- **표적/엔터티 감성:** 특정 대상에 대한 감성(뉴스 헤드라인 등)은 LLM이 유리한 경우.

---

## 5. 핵심 스킬

### 5-1. 데이터 & 불균형
- 정제·중복 제거·**라벨 일관성**이 성능의 8할. 
- **클래스 불균형:** 가중 CrossEntropy(class weights), focal loss, 오버/언더샘플링. **평가는 반드시 macro-F1**(정확도만 보면 다수 클래스에 속음).

### 5-2. 인코더 파인튜닝
- 학습률 2e-5~5e-5, warmup, epoch 2~4(과적합 빠름), `max_length` 태스크에 맞게(짧으면 128~256).
- **도메인 적응:** 도메인 코퍼스로 **연속 MLM 사전학습** 후 파인튜닝하면 향상.

### 5-3. 한국어 특성 (중요)
- **토크나이저 선택**이 성능 좌우: 노이즈 텍스트 → KcELECTRA 토크나이저.
- 형태소/음절 자질 활용, **구어체·신조어·은어·이모지·띄어쓰기 오류·초성** 대응. 필요 시 KoNLPy(Mecab/Okt)·soynlp 전처리.
- **비꼼(sarcasm)·부정(negation)·코드스위칭**은 난제 — 데이터로 커버하거나 LLM 보조.

### 5-4. 소수/제로샷
- **SetFit:** 대조학습으로 문장 임베딩 미세조정 → 소수 예시로 강력.
- **제로샷:** NLI 가설-전제 방식, 또는 LLM 프롬프트.

### 5-5. 평가 & 해석
- accuracy, **macro-F1(주지표)**, weighted-F1, 클래스별 F1, 혼동행렬, 캘리브레이션.
- **설명성:** SHAP·LIME·Captum·transformers-interpret로 토큰 기여도 시각화.

### 5-6. 8GB 최적화
- fp16/bf16(AMP), gradient accumulation, `max_length` 축소, dynamic padding. 인코더는 대개 여유.

---

## 6. 최적화된 툴체인

```bash
python -m venv venv && source venv/bin/activate
pip install -U pip

# 핵심: 인코더 파인튜닝
pip install transformers datasets accelerate evaluate scikit-learn

# 소수 샷 분류
pip install setfit sentence-transformers

# LLM 트랙(QLoRA)
pip install peft bitsandbytes trl
pip install unsloth            # 8GB LLM 파인튜닝 가속

# 한국어 전처리(선택)
pip install konlpy soynlp

# 해석성
pip install shap transformers-interpret

# 배포
pip install onnx onnxruntime-gpu
```

| 범주 | 도구 | 역할 |
|---|---|---|
| 인코더 학습 | **Transformers + datasets** | `AutoModelForSequenceClassification` + `Trainer` |
| 소수 샷 | **SetFit** | 라벨 극소량 분류 |
| 제로샷 | transformers `zero-shot-classification` | NLI 기반 |
| LLM | PEFT + bitsandbytes + **Unsloth** | QLoRA 파인튜닝 |
| 한국어 | KoNLPy / soynlp | 형태소·정제 |
| 평가/해석 | scikit-learn / SHAP | macro-F1·토큰 기여 |
| 배포 | ONNX Runtime | 경량·고속 추론 |

---

## 7. 코드 스켈레톤

### 7-1. 한국어 인코더 파인튜닝 (KcELECTRA)

```python
from transformers import (AutoTokenizer, AutoModelForSequenceClassification,
                          TrainingArguments, Trainer)
import numpy as np, evaluate

MODEL = "beomi/KcELECTRA-base"   # 댓글/리뷰 → Kc*, 표준문어 → klue/roberta-base
tok = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL, num_labels=NUM_LABELS)

def preprocess(ex): return tok(ex["text"], truncation=True, max_length=256)
# dataset = load_dataset(...).map(preprocess, batched=True)

f1 = evaluate.load("f1")
def metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return f1.compute(predictions=preds, references=p.label_ids, average="macro")

args = TrainingArguments(
    output_dir="out", learning_rate=3e-5, num_train_epochs=3,
    per_device_train_batch_size=16, per_device_eval_batch_size=32,
    fp16=True, eval_strategy="epoch", metric_for_best_model="f1",
    load_best_model_at_end=True,
)
# class weights로 불균형 대응 시 커스텀 loss 사용
trainer = Trainer(model=model, args=args, train_dataset=..., eval_dataset=...,
                  compute_metrics=metrics)
trainer.train()
```

### 7-2. SetFit 소수 샷

```python
from setfit import SetFitModel, Trainer as SFTrainer
model = SetFitModel.from_pretrained("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
# 클래스당 8~16개 예시로도 학습 가능
```

### 7-3. 제로샷 (라벨 없이)

```python
from transformers import pipeline
zsc = pipeline("zero-shot-classification", model="joeddav/xlm-roberta-large-xnli")
zsc("배송이 너무 느리고 포장도 엉망이에요", candidate_labels=["긍정","부정","중립"])
```

---

## 8. 멀티에이전트 통합

- **감정 에이전트로 래핑:** 입력=텍스트, 출력=`{sentiment, score, confidence, emotions[], aspects[]}` JSON.
- **★ 인코더+LLM 하이브리드(비전 스택과 동일 패턴):** 인코더가 **1차 고속 분류** → confidence 낮거나 경계·비꼼 의심 케이스만 **LLM이 근거와 함께 재판정**. 8GB에서 인코더는 상주, LLM은 필요 시 호출.
- **측면 기반 라우팅:** 측면 추출 → 측면별 감성 → 집계 리포트(예: "배송=부정, 품질=긍정").
- **★ 멀티모달 연계(비전 스택과 결합):** VLM/OCR로 이미지→텍스트 → 감정 분석, 또는 이미지 감성(비전) + 캡션 감성(NLP)을 결합한 **멀티모달 감성.** 리뷰의 사진+글을 함께 분석.
- **닫힌 루프·능동학습:** 저신뢰 샘플을 사람이 라벨 → 재학습(active learning)으로 지속 개선.
- **용도:** 고객 피드백/VOC, SNS 모니터링, 리뷰 분석 → 하위 **응답·에스컬레이션 에이전트**로 전달.

---

## 9. 함정 체크리스트

- [ ] 정확도만 보고 불균형 무시 → **macro-F1** 확인.
- [ ] 표준 문어 모델(KLUE)로 댓글 분석 → 노이즈에 약함. **KcELECTRA** 사용.
- [ ] 다중 감정을 다중 클래스로 강제 → 다중 라벨은 **sigmoid+BCE**.
- [ ] `max_length` 과대 설정 → 느리고 메모리 낭비. 태스크 길이에 맞게.
- [ ] 비꼼·부정 표현 미대응 → 데이터 보강 또는 LLM 보조.
- [ ] 분류에 무조건 대형 LLM → 느리고 비쌈. **인코더가 대개 더 낫다.**
- [ ] 도메인 시프트 방치 → 연속 MLM 사전학습으로 적응.

---

## 10. 파일명 추천

- **1순위 (영문):** `nlp-sentiment-analysis-transformer-guide.md` *(현재 파일명)*
- 대안:
  - `sentiment-analysis-modernbert-korean-rtx3060ti.md`
  - `nlp-sentiment-agent-setup.md`
  - 한글 선호 시: `자연어처리_감정분석_가이드.md`

> 세트 구성(멀티에이전트 스택 8종): 비전 7종 + `nlp-sentiment-analysis-transformer-guide.md`(NLP 컴포넌트).