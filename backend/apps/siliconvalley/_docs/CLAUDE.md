# Silicon Valley App — Harness & Architecture (`backend/siliconvalley`)

Parent specs:

- Backend: [`../../../CLAUDE.md`](../../../CLAUDE.md)
- 형제 앱 참고: [`../../titanic/_docs/CLAUDE.md`](../../titanic/_docs/CLAUDE.md)

**Physical root:** `backend/apps/siliconvalley/` · **Import prefix:** `siliconvalley.*`  
**도메인 테마:** TV 「Silicon Valley」의 **Piper** 크루 — 관리자 대시보드·데모 캐릭터 API

---

## Fractal layout (hexagonal + clean + DDD)

```
backend/apps/siliconvalley/
├── _docs/
│   └── CLAUDE.md               # 이 문서 (앱 SSOT)
├── domain/
│   ├── constants/              # 도메인 상수 (예약)
│   ├── entities/               # *_entity.py — 스텁
│   └── value_objects/          # VO 슬롯 — AOP 확정 전 비움
├── app/
│   ├── ports/
│   │   ├── input/              # *_use_case.py
│   │   └── output/             # *_port.py
│   ├── use_case/               # *_interactor.py  (※ titanic은 use_cases/)
│   └── dtos/                   # Query·Response DTO
├── adapter/
│   ├── inbound/
│   │   ├── api/
│   │   │   ├── __init__.py     # piper_router 집계
│   │   │   ├── schemas/        # *_schema.py (Pydantic)
│   │   │   └── v1/             # *_router.py
│   │   └── Assemblers/         # Schema ↔ DTO (inbound 경계)
│   └── outbound/
│       ├── mappers/            # ORM ↔ domain
│       ├── orm/                # *_orm.py
│       └── repositories/       # *_repository.py
└── dependencies/               # *_provider.py
```

---

## 런타임 호출 체인

**안쪽 통로** (`Router` ~ `Repository` 인터페이스 구간)는 **DTO/Entity 전용**이다.  
**Assembler·Mapper는 체인의 한 “층”이 아니다** — Router·Repository **경계(톨게이트)** 에서만 타입을 갈아입힌다.

```
Router → UseCase → Interactor → Port → Repository → (outbound Mapper → ORM → DB)
```

| 단계 | 역할 |
|------|------|
| **Router** | HTTP·`Depends(get_*_use_case)`. 진입/반환 시 **Assembler**로 Schema ↔ DTO |
| **UseCase** | Input port 추상 (`*_use_case.py`) |
| **Interactor** | UseCase 구현. **DTO/Entity만** — Schema·ORM 모름 |
| **Port** | Output port 추상 (`*_port.py`) |
| **Repository** | Port 구현. DB 시 **Mapper**로 ORM ↔ Entity/DTO |

**DIP:** Router → Repository 직접 호출 금지 · Schema/ORM이 Interactor·UseCase·domain 안으로 직행 금지.

### 타입·변환 (경계 톨게이트)

| 경계 | 변환 담당 | 방향 | 안쪽에서 쓰는 타입 |
|------|-----------|------|-------------------|
| HTTP 진입 | **Assembler** (`adapter/inbound/Assemblers/`) | `Schema` → `QueryDTO` | DTO |
| HTTP 응답 | **Assembler** | `ResponseDTO` → `Schema` | DTO |
| DB 저장 | **Mapper** (`adapter/outbound/mappers/`) | `Entity`/DTO → `ORM` | Entity/DTO |
| DB 조회 | **Mapper** | `ORM` → `Entity`/DTO | Entity/DTO |

| 타입 | 분류 | 위치 |
|------|------|------|
| `Schema` | 경계 (HTTP) | `adapter/inbound/api/schemas/` |
| `DTO` | 안쪽 전용 | `app/dtos/` |
| `Entity` (+ VO) | 안쪽 전용 | `domain/entities/`, `domain/value_objects/` |
| `ORM` | 경계 (DB) | `adapter/outbound/orm/` |

> **원칙:** Schema·ORM은 Assembler/Mapper 없이 안쪽에 들어오거나 나가면 안 된다.  
> titanic의 *inbound mapper* = siliconvalley의 **Assembler** (같은 경계 책임).

- **데모:** Repository가 ORM 없이 DTO만 반환 → Mapper·ORM 스텁.
- **잘못된 그림:** `Router → Assembler → UseCase` (Assembler를 별도 레이어로 적기) ❌
- **맞는 그림:** Router **안에서** Assembler 호출 후 `await use_case.method(dto)` ✅

| 레이어 | 책임 | 금지 |
|--------|------|------|
| **Inbound** | HTTP·Schema·**Assembler** | 비즈니스 규칙·SQL |
| **Application** | UseCase·Interactor·**DTO** | FastAPI `Depends`, ORM, Schema |
| **Domain** | 엔티티·VO·상수 | FastAPI, SQLAlchemy |
| **Outbound** | Repository·**Mapper**·ORM | `HTTPException` |
| **dependencies/** | Composition root | 도메인 로직 |

---

## 프랙탈 네이밍 — `piper_` 캐릭터

| 접두 | 의미 | 예 |
|------|------|-----|
| `piper_` | Piper 크루 capability | `piper_bighetti_hr` |

| 캐릭터 | 파일 stem | 역할 | HTTP (v1) |
|--------|-----------|------|-----------|
| Bighetti | `piper_bighetti_hr` | HR | `GET /api/piper/bighetti/myself` |
| Dinesh | `piper_dinesh_dash` | 대시보드 | `GET /api/piper/dinesh/myself` |
| Dunn | `piper_dunn_coo` | COO | `GET /api/piper/dunn/myself` |
| Gilfoyle | `piper_gilfoyle_sys` | 시스템 | `GET /api/piper/gilfoyle/myself` |
| Hendricks | `piper_hendricks_ceo` | CEO | `GET /api/piper/hendricks/myself` |

| Layer suffix | Example (`bighetti`) |
|--------------|----------------------|
| `_router` | `piper_bighetti_hr_router.py` → `bighetti_router` |
| `_schema` | `piper_bighetti_hr_schema.py` → `BighettiHrSchema` |
| `_assembler` | `piper_bighetti_hr_assembler.py` |
| `_use_case` | `piper_bighetti_hr_use_case.py` → `BighettiHrUseCase` |
| `_interactor` | `piper_bighetti_hr_interactor.py` |
| `_port` | `piper_bighetti_hr_port.py` → `BighettiHrPort` |
| `_repository` | `piper_bighetti_hr_repository.py` |
| `_orm` | `piper_bighetti_hr_orm.py` |
| `_mapper` | `piper_bighetti_hr_mapper.py` |
| `_dto` | `piper_bighetti_hr_dto.py` |
| `_provider` | `piper_bighetti_hr_provider.py` |
| `_entity` | `piper_bighetti_hr_entity.py` |

새 캐릭터 추가 시 **위 stem 전체를 한 세트**로 복제·치환 + `piper_router`에 `include_router`.

---

## Domain — Entity·VO

### Entity (`domain/entities/`)

- 캐릭터별 `*_entity.py` **자리만** (`pass` 스텁).
- 영속 모델·비즈니스 불변식이 생기면 여기로 옮긴다.

### Value Object (`domain/value_objects/`)

- **폴더만 있고 파일·명칭은 아직 없음.**
- **AOP(Aspect-Oriented Programming)** 와 함께 VO·횡단 관심사(페르소나·로깅·검증 등) 경계를 정한 뒤 구현한다.
- **하네스 1단계:** 레이어·호출 흐름·`piper_*` 네이밍만 고정. AOP/VO SSOT는 의도적으로 비움.
- VO를 임의로 `*_vo.py`로 채우지 말고, 규칙이 정해지면 **이 문서에 명칭·책임을 먼저 기록**한 뒤 구현한다.

---

## 표준 호출 흐름 (`introduce_myself`)

### 방향 ① 외부 입력 (HTTP → DB)

```
Schema ──[Assembler]──▶ QueryDTO ──▶ Router ──▶ UseCase ──▶ Interactor
  ──▶ Port ──▶ Repository ──[Mapper]──▶ ORM ──▶ DB
```

```
Router.introduce_myself
  character: BighettiHrUseCase = Depends(get_bighetti_use_case)
  query = schema_to_query(...)                    # Assembler: Schema → DTO
  dto = await character.introduce_myself(query)   # Interactor → Port → Repository
  return response_to_schema(dto)                  # Assembler: DTO → Schema
```

### 방향 ② DB 조회 (DB → HTTP)

```
DB ──▶ ORM ──[Mapper]──▶ Entity(+VO) ──▶ Repository ──▶ Port
  ──▶ Interactor ──▶ UseCase ──▶ Router ──[Assembler]──▶ Schema ──▶ HTTP 응답
```

| 방향 | ❌ 위반 | ✅ 올바름 |
|------|---------|----------|
| ① 외부 입력 | `await use_case.introduce_myself(Schema(...))` | `schema_to_query` 후 `QueryDTO` 전달 |
| ② DB 조회 | ORM을 그대로 위로 올려 Schema로 응답 | ORM → Mapper → Entity/DTO → … → Assembler → Schema |

**비동기:** I/O 있는 메서드는 `async def` + `await`.

---

## HTTP surface

| Item | Value |
|------|-------|
| Aggregator | `siliconvalley.adapter.inbound.api.piper_router` |
| Mount | `main.py` → `prefix="/api"` |
| Tags | `piper`, 캐릭터별 `bighetti` … |

**Frontend BFF:** `frontend/app/api/piper/[...path]/route.ts` (로컬은 `next.config.mjs` rewrite도 가능)

**관리자 UI:** `frontend/app/admin/siliconvalley/` · `frontend/lib/admin/siliconvalley-client.ts`

---

## titanic 형제 앱과의 차이

| 항목 | titanic | siliconvalley |
|------|---------|---------------|
| capability 접두 | `crew_`, `passenger_` | `piper_` |
| Interactor 경로 | `app/use_cases/` | `app/use_case/` |
| Inbound 변환 | `adapter/inbound/mappers/` | `adapter/inbound/Assemblers/` |
| 도메인 성숙도 | entity·VO 사용 중 | entity·VO **스텁·예약** |
| 1차 API | chat, upload, ML 등 | `introduce_myself` 데모 |

의도적 차이가 아니면 새 작업은 **titanic 관례**로 점진 정렬 검토.

---

## 하네스 메모

1. **성공 기준 먼저:** `GET /api/piper/dinesh/myself` → `{ id, name }` 200.
2. **프랙탈 복제:** 캐릭터 1명 = stem 세트 전체 + `piper_router`.
3. **최소 diff:** Interactor는 repository 위임만; 규칙은 domain·VO 확정 후.
4. **검증:** `/docs` · `curl` · `/admin/siliconvalley` Piper 카드.
5. **VO / AOP:** 확정 전 `domain/value_objects/`에 파일 추가 금지.

## Acknowledgment

`_docs acknowledged: Backend harness + siliconvalley _docs/CLAUDE.md`
