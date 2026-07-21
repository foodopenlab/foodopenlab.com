# Backend Harness & Architecture (`backend`)

> **SSOT:** 이 파일은 [`backend/_docs/CLAUDE.md`](CLAUDE.md) 입니다.  
> 코드 트리 [`backend/CLAUDE.md`](../CLAUDE.md) 는 이 파일을 가리키는 **포인터**입니다. 여기만 수정하면 AI·개발자가 동일 문서를 봅니다.

Parent: [`../../CLAUDE.md`](../../CLAUDE.md)

**Backend 전용 문서는 this folder (`backend/_docs/`).**

**Physical root:** `com.foodopenlab/backend/` · **PYTHONPATH:** `apps/` + `core/` (`main.py`가 주입)

---

## Monorepo 위치

| Item | Path |
|------|------|
| FastAPI entry | `backend/main.py` |
| Domain apps | `backend/apps/{domain}/` |
| Shared core | `backend/core/matrix/` |
| Alembic | `backend/alembic/` |
| Docker backend | `docker-compose.yaml` → `fastapi_backend` :8000 |
| Env | `backend/.env` |

**등록된 주요 라우터 (`main.py`):**

| Import prefix | App | Mount |
|---------------|-----|-------|
| `mfds_user.*` | MFDS 사용자 API | `user_router` |
| `mfds_admin.*` | MFDS 관리자 API | `admin_router` |
| `titanic.*` | Titanic 학습/데모 | `titanic_router` → `/api/titanic/...` |
| `siliconvalley.*` | Piper 크루 (실리콘밸리) | `piper_router` → `/api/piper/...` |

기타 `apps/` 형제: `imitation_game`, `inception`, `social_network` 등 — 동일 프랙탈 패턴으로 `_docs/` 추가.

---

## App-level specs (sibling apps)

```
backend/apps/{domain}/_docs/CLAUDE.md
```

| App | Spec |
|-----|------|
| titanic | [`apps/titanic/_docs/CLAUDE.md`](../apps/titanic/_docs/CLAUDE.md) |
| siliconvalley | [`apps/siliconvalley/_docs/CLAUDE.md`](../apps/siliconvalley/_docs/CLAUDE.md) |
| mfds_user | [`apps/mfds_user/_docs/CLAUDE.md`](../apps/mfds_user/_docs/CLAUDE.md) |
| mfds_admin | [`apps/mfds_admin/_docs/CLAUDE.md`](../apps/mfds_admin/_docs/CLAUDE.md) |

앱 작업 시: **this file + 해당 앱 `_docs/CLAUDE.md`**.

**PKS (이 폴더 하위 위키):** [`db-rules.md`](db-rules.md) · [`auth-rules.md`](auth-rules.md) · [`entity-rules.md`](entity-rules.md) · [`scaffold-rules.md`](scaffold-rules.md) · [`mfds-erd.md`](mfds-erd.md)

---

## Architecture — SOLID + Hexagonal + Clean + DDD

All backend feature work **must** comply with:

- **SOLID** (especially DIP: depend on ports, not concrete adapters)
- **Hexagonal** (inbound vs outbound; adapters at edges)
- **Clean** (dependency rule: domain has no framework imports)
- **DDD** (entities/VOs; application orchestrates use cases)

| Layer | Responsibility | Must NOT |
|-------|----------------|----------|
| **Inbound adapter** (router, schema, inbound mapper) | HTTP 검증, Schema↔DTO 변환 | SQL, ORM, 비즈니스 규칙 |
| **Application** (use case port, interactor, dto) | 유스케이스 오케스트레이션 | FastAPI `Depends`, ORM |
| **Domain** (entity, value object) | 도메인 규칙·타입 | FastAPI, SQLAlchemy, HTTP |
| **Outbound adapter** (repositories/memory/orm, outbound mapper) | 영속성·외부 I/O | `HTTPException` (라우터 책임) |
| **dependencies/** | Composition root — `get_*_repository` → `get_*_use_case` | 비즈니스 로직 |

**표준 호출 흐름:**

```
Router → Schema → (inbound mapper) → Query/Command DTO
      → UseCase (abstract) → Interactor → Output port (abstract) → Repository
      → Response DTO → Router → Response Schema
```

**DIP 금지:**

- Router → `*Repository` (adapter) 직접 import
- Interactor → `Depends`, inbound `*Schema` (DTO/Command 사용)
- Domain → framework import

**Fractal naming:** 동일 capability 접두·접미 (`crew_smith_captain_router`, `_schema`, `_dto`, `_interactor`, `_port`, `_repository`, `_provider`).

### Use case · interactor — `async` 붙일까?

**같은 use case 클래스 안에서도 메서드마다 다를 수 있다.** `async`는 “클래스가 async라서”가 아니라 **안에서 `await`할 I/O가 있을 때만** 붙인다.

| 메서드 성격 | 예 | use case / interactor |
|-------------|-----|------------------------|
| **CPU-bound** — 동기 연산만, DB·네트워크·파일 없음 | Kiwi `tokenize()`, dict 점수 계산 (`analyze_intent`) | `def` |
| **I/O-bound** — DB·LLM·HTTP·파일 등 `await` 필요 | `repository.introduce_myself(...)`, 외부 API | `async def` |

**금지:** CPU만 하는 메서드에 `async def`만 달고 내부에 `await` 없음 → 코루틴만 생기고 **이벤트 루프는 그대로 블로킹**. 비동기인 것처럼 보이지만 실제로는 더 헷갈리는 동기 코드가 된다.

**CPU가 무거워 이벤트 루프 블로킹이 문제일 때** — port를 `async def`로 바꾸기보다 **호출 측(router 등)** 에서 스레드풀 위임:

```python
result = await asyncio.to_thread(use_case.analyze_intent, question)
```

참고 예 (`titanic`): `analyze_intent` → `def` · `introduce_myself` → `async def` (repository I/O `await`).

**에이전트:** 오류 수정 시 use case/interactor의 **동기·비동기 시그니처를 임의로 바꾸지 않는다.** 레이어·책임(예: interactor ↔ repository)도 사용자 요청 없이 옮기지 않는다.

---

## Star Topology (Star-Craft) — Hub & Spoke Architecture

> **Hub 앱 = `apps/ontology/`.** "Star-Craft"는 이 토폴로지/파이프라인의 **코드명**이며 앱 이름이 아니다. `apps/star_craft/`는 존재하지 않는다.
> 근거(3개 SSOT 일치): master [`../../CLAUDE.md`](../../CLAUDE.md) §11 · `apps/ontology/_docs/star-craft-pipeline.md` frontmatter(`type: hub, domain: ontology`) · `apps/braindead/_docs/rule.md`("온톨로지 버스 Ontology Hub: `apps/ontology`").

### 개념

기존 **선형 클린 아키텍처(Clean Architecture)** 위에 **비선형 스타 토폴로지(Star Topology)** 레이어를 추가한다.  
이는 Karpathy 하네스 엔지니어링의 정신을 아키텍처 의존성 제어에 적용한 패러다임 시프트다:  
복잡한 비선형 앱 간 연결이 깨지지 않도록 의존성 규칙을 **코드·문서 양쪽에서 동시에 강제**한다.

```
        [mfds_user]   [mfds_admin]
             ↑              ↑
[titanic] → [ontology HUB] ← [siliconvalley]
                  ↑
             [braindead]

계획됨(미구현): imitation_game · inception · social_network
```

### Hub — `apps/ontology/`

- **역할:** 지식 교차점, 온톨로지 상위 개념, 컨텍스트 라우팅, 전역 인덱스/상태 관리 (전사 데이터 흐름·엔티티 관계 버스)
- **허용:** `ontology` → `{any spoke}` (Hub가 Spoke를 알고 오케스트레이션)
- **허용:** `{any spoke}` → `ontology` (Spoke가 Hub에 등록·위임)
- **금지:** `{spoke_A}` → `{spoke_B}` 직접 참조 — 반드시 Hub 경유

### Spokes — 나머지 apps

| Spoke | 도메인 | 상태 |
|-------|--------|------|
| `mfds_user` | MFDS 사용자 | 구현됨 |
| `mfds_admin` | MFDS 관리자 | 구현됨 |
| `braindead` | 메시징 채널 (Email·Telegram·Discord) | 구현됨 |
| `titanic` | ML 학습/데모 | 구현됨 |
| `siliconvalley` | Piper 크루 | 구현됨 |
| `imitation_game` | 이미테이션 게임 | 계획됨 |
| `inception` | 인셉션 | 계획됨 |
| `social_network` | 소셜 네트워크 | 계획됨 |

> `apps/sample`(프랙탈 스캐폴드 템플릿)·`apps/adapters`(`db_health_adapter`)는 BC 스포크가 아니다.

### 하네스 의존성 규칙 (Non-Negotiable)

```
허용: ontology   → {any spoke}     # Hub orchestrates
허용: {any spoke} → ontology        # Spoke registers to Hub
금지: {spoke_A}   → {spoke_B}       # Spoke↔Spoke 직접 참조 금지
금지: ontology 내 순환 참조          # Hub 자체 circular import 금지
```

위반 즉시 탐지 (CI 또는 수동):

```bash
# spoke→spoke 직접 참조 탐지 (예시)
grep -rE "(from|import) +mfds_admin" apps/mfds_user/
grep -rE "(from|import) +mfds_user"  apps/mfds_admin/
```

### MD 온톨로지 메타데이터 (Frontmatter 규칙)

`_docs/` 내 MD 파일이 토폴로지 노드를 표현할 때 아래 frontmatter를 **필수** 포함한다:

```yaml
---
type: hub          # hub | spoke
domain: ontology   # 앱 이름 (hub는 ontology, spoke는 자신의 도메인명)
links:             # 연결 노드 (spoke는 ontology만 기재)
  - ontology
---
```

- `type: hub` → `ontology` 전용
- `type: spoke` → `links`에 `ontology` 반드시 포함
- Spoke MD에서 타 Spoke를 `links`에 직접 기재 금지

### Harness Validation 체크리스트

| # | 검증 항목 | 판정 기준 |
|---|-----------|-----------|
| 1 | Spoke 내 타 Spoke `import` | 발견 시 즉시 리젝 |
| 2 | MD Frontmatter (`type`, `domain`, `links`) 누락 | 경고·리포트 |
| 3 | 고립 노드 (Hub·Spoke 미연결 MD) | 경고 |
| 4 | Hub 내 순환 참조 | 즉시 리젝 |

> 자동화 스크립트: `backend/scripts/validate-harness.py` (추후 구현)
> **현재 알려진 위반(#1):** `mfds_user ↔ mfds_admin` 양방향 직접 참조 — 화이트리스트 ORM·`security.verify_password` 공유. Hub(`ontology`) 경유 또는 공유 커널(`core/`)로 해소 필요. `ontology → mfds_user`(law_chunk RAG)는 Hub→Spoke라 위상상 허용이나, 포트 대신 ORM 내부를 직접 참조하는 결합은 개선 여지.

---

## Path & Import Conventions

| Kind | Documentation path | Physical path |
|------|-------------------|---------------|
| App/domain | `backend/{domain}/...` | `backend/apps/{domain}/...` |
| Core | `backend.core.*` | `backend/core/matrix/...` |

**Python imports:** `titanic.*`, `mfds_user.*`, `mfds_admin.*`, `matrix.*` (저장소 관례 유지).

---

## Stack & operations

| Topic | Rule |
|-------|------|
| HTTP | Pydantic schema; 400/404/409/502/503 + 짧은 `detail` |
| Env | `.env` / Keymaker; 비밀 커밋 금지 |
| External API | cache-first; background enrich (`mfds_user` lifecycle) |
| DB schema | **Alembic SSOT**; `db_init` = 존재 확인·dev helper |
| Docker | deps 변경 → `docker compose up -d --build backend`; `.py`만 → `restart backend` |
| LLM (titanic 등) | blocking I/O → `asyncio.to_thread`; Docker → `OLLAMA_HOST=host.docker.internal:11434` |

---

## 머신러닝 데이터 분석 원칙

피처·스키마·전처리 설계 시 **측정 척도**를 먼저 구분한다.

### Categorical (범주형)

데이터가 카테고리로 묶일 때 사용한다.

| 척도 | 설명 | 예 |
|------|------|-----|
| **nominal** (명목) | 이름을 바탕으로 하는 척도. 순서와 무관하게 셀 수 있는 데이터 | 청팀, 홍팀, 백팀 |
| **ordinal** (서열) | 순서를 바탕으로 하는 척도. 자료 사이에 순서(서열)가 있는 경우 | 청팀이 이길 가능성: 1. 매우 낮음 · 2. 낮음 · 3. 보통 · 4. 높음 · 5. 매우 높음 |

### Quantitative (양적)

숫자로 셀 수 있을 때 사용한다.

| 척도 | 설명 | 예 |
|------|------|-----|
| **interval** (등간) | 간격을 바탕으로 하는 척도. 임의의 원점 없이 일정한 측정 구간을 갖는 데이터 | 11:00~11:05, 15:55~16:00, 온도, pH — 「10배 덥다」「10배 시다」는 불가 |
| **ratio** (비율) | 비율을 바탕으로 하는 척도. 임의의 원점(0)을 기준으로 두는 데이터 | 나이, 돈, 몸무게 — 「10배 많다」가 가능 |

**적용:** nominal → one-hot·label encoding(순서 없음) · ordinal → 순서 보존 인코딩·순위 처리 · interval/ratio → 산술 연산·스케일링(원점 의미에 주의).

---

## Verification (backend)

1. `/docs` 또는 `curl` / reproducible API check  
2. `uvicorn` / `docker logs fastapi_backend`  
3. Lint/typecheck on touched modules  
4. `pytest apps/{domain}/tests` when applicable  
5. `alembic upgrade head` when ORM changes  

## Acknowledgment (one line)

`_docs acknowledged: backend/_docs/*.md (+ app _docs/CLAUDE.md if applicable)`
