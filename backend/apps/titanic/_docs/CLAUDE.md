# Titanic App — Harness & Architecture (`backend/titanic`)

Parent specs:

- Backend: [`../../../CLAUDE.md`](../../../CLAUDE.md)
- Monorepo 루트는 백엔드 harness 경유 — 직접 링크 없음 (`../../../../CLAUDE.md` 텍스트 참고만)

**Physical root:** `backend/apps/titanic/` · **Import prefix:** `titanic.*`

---

## Sibling app pattern

`titanic`은 `apps/` 아래 **형제 앱** 중 하나다. `mfds_user`, `mfds_admin` 등이 늘어나면 동일 패턴:

```
backend/apps/{domain}/_docs/CLAUDE.md
```

각 앱은 자체 프랙탈·라우터·문서를 갖고, **백엔드 공통**은 [`../../../CLAUDE.md`](../../../CLAUDE.md)를 따른다.

---

## Fractal layout (hexagonal + clean + DDD)

---> **앱별 아키텍처 상세는 루트/백엔드 명세에서 titanic 컨텍스트로 분리했습니다.**

```
backend/apps/titanic/
├── domain/
│   ├── entities/          # *_entity.py
│   └── value_objects/     # *_vo.py, persona constants
├── app/
│   ├── ports/input/       # *_use_case.py
│   ├── ports/output/      # *_port.py
│   ├── use_cases/         # *_interactor.py
│   └── dtos/              # *_dto.py
├── adapter/
│   ├── inbound/api/       # titanic_router, v1/*_router.py, schemas/
│   ├── inbound/mappers/   # schema → domain (inbound boundary)
│   └── outbound/          # orm/, repositories/, memory/, mappers/
└── dependencies/          # get_*_use_case — composition root
```

### Naming

| Prefix | Examples |
|--------|----------|
| `crew_` | `crew_smith_captain`, `crew_james_director` |
| `passenger_` | `passenger_jack_trainer`, `passenger_rose_model` |

| Layer suffix | Example |
|--------------|---------|
| `_router` | `crew_smith_captain_router.py` |
| `_schema` | `crew_smith_captain_schema.py` (`ChatSchema`, `SmithCaptainSchema`) |
| `_use_case` | `crew_smith_captain_use_case.py` |
| `_interactor` | `crew_smith_captain_interactor.py` |
| `_port` | `crew_smith_captain_port.py` (`SmithCaptainPort`) |
| `_repository` | `crew_smith_captain_repository.py` (`SmithCaptainRepository`) |
| `_provider` | `crew_smith_captain_provider.py` |

### Dependency rule (titanic)

```
HTTP → Router → UseCase (port) → Interactor → Output port → Repository / ORM
                     ↑                              ↑
              dependencies/                   domain only
```

**금지:** Router → Repository (adapter) · Interactor → `Depends` · Domain → FastAPI/SQLAlchemy.

---

## HTTP surface

| Item | Value |
|------|-------|
| Aggregator | `titanic.adapter.inbound.api.titanic_router` |
| Mount | `main.py` → `prefix="/api"` |
| Character routes | `/api/titanic/{name}/...` |

Examples: `POST /api/titanic/smith/chat`, `POST /api/titanic/james/upload`, `GET /api/titanic/jack/myself`

---

## Smith Captain chat (reference flow)

| Step | Component |
|------|-----------|
| Request | `ChatSchema` — `{ message }` |
| Router | `crew_smith_captain_router.chat` — injects `smith`, `jack`, `rose` via `Depends` |
| Use case | `SmithCaptainUseCase.chat(schema, jack, rose)` |
| Interactor | `repository.chat(schema.message)` |
| Repository | Kiwi preprocess → `get_stats()` → Ollama (Gemini fallback) |
| Response | `{ text, message_id, session_key }` (router maps from `SmithCaptainResponse`) |

**Frontend BFF:** `frontend/app/api/lesson/titanic/smith/chat/route.ts`

**Docker:** `OLLAMA_HOST=http://host.docker.internal:11434` or `GEMINI_API_KEY` in `backend/.env`

---

## Persistence

| Table | ORM | Role |
|-------|-----|------|
| `titanic_persons` | `JackTrainerOrm` | Passengers (James upload) |
| `titanic_bookings` | `RoseModelOrm` | Bookings |

Startup: `adapter/outbound/repositories/db_init.py` — table existence check; **Alembic** = schema SSOT.

---

## Acknowledgment (one line)

`_docs acknowledged: titanic _docs/CLAUDE.md`


## 타이타닉 도메인 문서 연결

* 타이타닉 도메인 문서 연결
* 타이타닉 피처 정리 [[titanic-features]]
* 타이타닉 머신러닝 [[titanic-machine-learning]]
* 타이타닉 ERD [[titanic-erd]]
* 타이타닉 알고리즘 [[titanic-algorithm]]
* 타이타닉 NF [[titanic-nf]]
* 타이타닉 뼈대(프랙탈 구조) [[titanic-bone]]
