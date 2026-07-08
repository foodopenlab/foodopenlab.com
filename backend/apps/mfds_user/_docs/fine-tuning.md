# 엑사온 LoRA 파인튜닝 — M5 Pro 셋업 가이드

> **목적:** 식품법규 채팅(regulation-chat)에서 엑사온이 MCP 조회 결과를 정확히 활용하도록 도메인 파인튜닝
> **하드웨어:** MacBook Pro M5 Pro / 64GB 통합 메모리 / 1TB SSD
> **프레임워크:** [MLX-LM](https://github.com/ml-explore/mlx-examples/tree/main/llms/mlx_lm) (Apple Silicon 최적화)

---

## 1. 환경 셋업

```bash
# Python 3.11+ 권장
brew install python@3.11

# 가상환경
python3.11 -m venv .venv
source .venv/bin/activate

# MLX-LM 설치
pip install mlx-lm

# 확인
python -c "import mlx; print(mlx.__version__)"
```

---

## 2. 베이스 모델 다운로드

```bash
# 엑사온 2.4b (현재 Docker에서 돌리는 것과 동일)
mlx_lm.convert \
  --hf-path LGAI-EXAONE/EXAONE-3.5-2.4B-Instruct \
  --mlx-path ./models/exaone-2.4b-mlx \
  -q  # 4-bit 양자화 (메모리 절약, 선택)

# 또는 7.8b (더 나은 품질)
mlx_lm.convert \
  --hf-path LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct \
  --mlx-path ./models/exaone-7.8b-mlx
```

> Hugging Face 토큰 필요 시: `huggingface-cli login`

---

## 3. 학습 데이터 준비

### 포맷 (JSONL)

파일 위치: `./data/train.jsonl`, `./data/valid.jsonl`

```jsonl
{"messages": [{"role": "system", "content": "당신은 한국 식품법규 전문 AI입니다. MCP로 조회한 법령 정보를 근거로만 답변하세요."}, {"role": "user", "content": "식품제조가공업에서 HACCP 의무 대상은?"}, {"role": "assistant", "content": "• 식품위생법 시행규칙 제62조에 따라 매출액 1억 원 이상 식품제조가공업체는 HACCP 의무 적용 대상입니다.\n• 단계적 의무화: 매출액 규모에 따라 적용 시기가 다릅니다.\n출처: 식품위생법 시행규칙 제62조, 별표 18"}]}
{"messages": [{"role": "system", "content": "당신은 한국 식품법규 전문 AI입니다. MCP로 조회한 법령 정보를 근거로만 답변하세요."}, {"role": "user", "content": "영양성분 표시 의무 대상 품목은?"}, {"role": "assistant", "content": "• 식품 등의 표시·광고에 관한 법률 제4조에 따라 가공식품은 영양성분 표시 의무가 있습니다.\n• 2026년부터 의무 대상이 259개 품목으로 확대됩니다.\n출처: 식품 등의 표시·광고에 관한 법률 제4조"}]}
```

### 데이터 소스 (우선순위순)

| 소스 | 방법 |
|------|------|
| 식약처 자주하는 질문집 PDF | PDF 파싱 → Q&A 쌍 추출 |
| 법제처 법령해석 사례집 | 법제처 사이트 다운로드 |
| 실제 채팅 로그 | DB에서 좋은 답변 레이블링 |
| 법령 조문 + 해설 | korean-law-mcp로 수집 |

최소 **200~500쌍** 이상 확보 권장. 도메인이 좁으면 100쌍도 효과 있음.

---

## 4. LoRA 파인튜닝 실행

```bash
mlx_lm.lora \
  --model ./models/exaone-2.4b-mlx \
  --train \
  --data ./data \
  --iters 1000 \
  --batch-size 4 \
  --lora-layers 16 \
  --learning-rate 1e-4 \
  --val-batches 25 \
  --save-every 100 \
  --adapter-path ./adapters/haccp-v1
```

| 파라미터 | 값 | 설명 |
|---------|-----|------|
| `--iters` | 1000 | 데이터 적으면 500도 충분 |
| `--lora-layers` | 16 | 높을수록 품질↑ 속도↓ |
| `--batch-size` | 4 | 64GB면 8까지 가능 |

**예상 소요 시간 (M5 Pro 64GB):**
- 엑사온 2.4b, 500 iter: ~15분
- 엑사온 7.8b, 1000 iter: ~1시간

---

## 5. 파인튜닝 결과 테스트

```bash
mlx_lm.generate \
  --model ./models/exaone-2.4b-mlx \
  --adapter-path ./adapters/haccp-v1 \
  --prompt "식품제조가공업에서 자가품질검사 주기는?"
```

---

## 6. Ollama 서빙 (Docker 연동)

어댑터를 병합해서 GGUF로 변환 후 Ollama에 등록합니다.

```bash
# 1. LoRA 어댑터 병합
mlx_lm.fuse \
  --model ./models/exaone-2.4b-mlx \
  --adapter-path ./adapters/haccp-v1 \
  --save-path ./models/exaone-2.4b-haccp-merged

# 2. GGUF 변환 (llama.cpp 필요)
brew install llama.cpp
llama-convert-hf-to-gguf ./models/exaone-2.4b-haccp-merged \
  --outfile ./models/exaone-2.4b-haccp.gguf \
  --outtype q4_k_m

# 3. Ollama Modelfile 생성
cat > Modelfile << 'EOF'
FROM ./exaone-2.4b-haccp.gguf
PARAMETER temperature 0.3
SYSTEM "당신은 한국 식품법규 전문 AI입니다. 법령 조회 결과를 근거로만 답변하고 없는 조문은 만들지 마세요."
EOF

# 4. Ollama 등록
ollama create exaone-haccp -f Modelfile

# 5. .env 업데이트
# EXAONE_MODEL=exaone-haccp
```

---

## 7. 현재 시스템 연동 포인트

파인튜닝 완료 후 `backend/.env`에서 모델명만 바꾸면 됩니다:

```env
# 기존
EXAONE_MODEL=exaone3.5:2.4b

# 파인튜닝 후
EXAONE_MODEL=exaone-haccp
```

코드 변경 없이 `regulation_chat_interactor.py`가 새 모델을 바라봅니다.

---

## 현재 아키텍처 (참고)

```
regulation-chat UI
  └─ Next.js BFF (route.ts)
       └─ FastAPI /regulation-chat
            └─ RegulationChatInteractor
                 ├─ KoreanLawMcpAdapter → korean-law-mcp → 법제처 API
                 │    ├─ amendment_track  ("최근/개정/변경" 키워드)
                 │    ├─ action_basis     ("처분/과징금/위반" 키워드)
                 │    ├─ law_system       ("체계/시행령" 키워드)
                 │    └─ search_laws      (그 외 키워드)
                 └─ ChatOllama → exaone3.5:2.4b (← 파인튜닝 후 교체)
```

---

## 8. 모델 선택 고민 메모

### 엑사온 대안 검토

| 모델 | 출처 | 한국어 | RAG 정확도 | 비고 |
|------|------|--------|-----------|------|
| Qwen2.5-7B-Instruct | 알리바바 | ★★★★☆ | ★★★★★ | 1순위 대안 |
| SOLAR-mini/10.7B | Upstage (한국) | ★★★★★ | ★★★★☆ | 법률 도메인 특화 |
| Gemma 3 12B | Google | ★★★☆☆ | ★★★★☆ | MLX 공식 지원 |

### Qwen2.5-7B 데이터 보안
- **로컬 Ollama 실행 = 데이터 알리바바 서버로 전송 없음**
- 위험한 경우는 Dashscope API 사용 시. 현재 아키텍처(로컬 Ollama)는 안전.

### 엑사온 + Qwen 혼합 방식 검토
- **파이프라인(직렬):** Qwen이 법령 컨텍스트 구조화 → Exaone이 한국어 답변 생성. 지연 2배.
- **라우팅:** 질문 유형별 모델 분기. 기준 세우기 어려움.
- **앙상블:** 두 모델 출력 + Judge LLM. 복잡도 대비 실익 낮음.
- **결론:** Qwen 단독 + LoRA 파인튜닝이 가장 단순하고 효과적. 혼합은 실제 품질 문제 확인 후 검토.

### Kiwi 형태소 분석기 연동 검토
- 붙이는 위치: 모델 내부 X → **MCP 도구 라우팅 전처리**에 활용
- 효과: 어미 변형("개정됐나요?" → "개정"), 조사 제거("과징금에 대해서" → "과징금") → 라우팅 정확도 향상
- 한계: LLM 한국어 생성 품질에는 직접 영향 없음
- **결론:** 현재 키워드 기반 라우팅 오류가 실제 발생하면 도입. 그 전까지는 오버엔지니어링.

### 권장 진행 순서
1. Qwen2.5-7B 단독으로 현재 시스템 연결 후 품질 측정
2. 한국어 품질 미달 시 LoRA 파인튜닝 (§4 절차 동일 적용)
3. MCP 라우팅 오류 발생 시 Kiwi 전처리 추가
4. 그래도 부족하면 파이프라인 혼합 방식 검토
