# Architecture & Stack — com.foodopenlab

> 식품안전(HACCP/MFDS) 플랫폼. 현재 구현 기준 핵심 요약 (2026-07-16).
> 상세 규약은 [`/CLAUDE.md`](../CLAUDE.md) 및 각 `_docs/` 참조.

---

## 0. 한눈에

- **모노레포**: `backend/`(FastAPI) + `frontend/`(Next.js), 도커 컴포즈로 통합 구동.
- **아키텍처 원칙**: Hexagonal + Clean Architecture + DDD 를 **프랙탈**로 반복 (모든 도메인이 같은 내부 형태).
- **배포**: 프론트 → Vercel(`foodopenlab.com`), 백엔드 → Docker + Cloudflare Tunnel(`api.foodopenlab.com`).

---

## 1. Backend (`backend/`)

### 스택
| 영역 | 기술 |
|---|---|
| 웹 | **FastAPI 0.136** + Uvicorn |
| ORM/DB | **SQLAlchemy 2.0 (async)** + Alembic, **PostgreSQL 17 + pgvector** |
| 캐시/큐 | **Redis 8** (crawl 시드·큐, rate limit, scout 이력) |
| 그래프 | **Neo4j 5.18** |
| LLM | **Gemini**(google-genai), **EXAONE**(Ollama / langchain-ollama) |
| 임베딩 | **bge-m3**(transformers) → pgvector RAG |
| 인증 | **PyJWT**(HS256), 사용자/관리자 분리 |
| 스케줄 | APScheduler(일일 리포트) |

### 아키텍처 — Modular Monolith + Fractal
```
backend/
├── core/matrix/     ← 전역 인프라 (grid_*_manager: DB·Redis·Secret·Embedding·Admin guard …)
└── apps/            ← Bounded Context 모음 (Star Topology, ontology = Hub)
```
- **의존성 방향**: `apps → core` (core는 apps를 모름). Spoke→Spoke 직접 참조 금지.
- **Fractal 11-File Set**: 1 테이블 = 1 AI 위임 단위.
  `router → use_case(input port) → interactor → port(output port) → repository`
  경계 변환: inbound `mapper`(schema↔dto), outbound `orm_mapper`(entity↔ORM).
- **레이어 규칙**: `domain/`·`app/use_cases/`는 FastAPI·SQLAlchemy import 금지 (의존성 내부 방향).
- **분기 처리**: 타입/상태 `if/elif` 대신 GoF 패턴(dispatch table 등).

### Bounded Contexts (`apps/`)
| 앱 | 역할 |
|---|---|
| **ontology** (Hub) | 시맨틱 게이트웨이(`/gateway/ask`, RAG/검색/일반/차단 라우팅), 비전, **크롤러·스크래퍼·스카우트** |
| **mfds_admin** | 어드민 인증(JWT)·대시보드·화이트리스트·로그 |
| **mfds_user** | 사용자 인증·마이페이지·업종/관심 설정·리포트 |
| **braindead** | 메시징 자동화(Gmail·Telegram·Discord, n8n 연동) |
| **siliconvalley** | piper 도메인 |
| **titanic** | 수업용 예제 도메인 |

---

## 2. Frontend (`frontend/`)

### 스택
| 영역 | 기술 |
|---|---|
| 프레임워크 | **Next.js 16 (App Router)** — 빌드/실행 모두 **webpack** (`--webpack`) |
| 언어/런타임 | **TypeScript 5.7**, **React 19** |
| 스타일 | **Tailwind CSS v4** |
| UI | **shadcn/ui** (Radix primitives) + lucide-react 아이콘 |
| 폼/검증 | react-hook-form + zod |
| 기타 | recharts(차트), next-themes(다크모드), sonner(토스트) |

### 아키텍처 — BFF 프록시
```
브라우저 ── same-origin /api/* ──► Next Route Handler / rewrite ──► FastAPI
```
| 레이어 | 책임 |
|---|---|
| `app/**/page.tsx` | Route UI (조합 중심, 로직 최소) |
| `app/api/**/route.ts` | **BFF** — FastAPI 프록시, 시크릿 은닉, 토큰 전달 |
| `components/` | 재사용 UI |
| `lib/` | API 경로, 백엔드 오리진, admin 인증(`adminFetch`) |

- **원칙**: 브라우저는 **same-origin `/api/*` 만** 호출 (백엔드 직접 호출 금지).
- **백엔드 오리진**: `resolveBackendOrigin()` — 프로덕션은 공개 URL만 허용(사설·터널 임시도메인 차단).
- **Admin 인증**: `adminFetch`가 JWT를 헤더로 전달, 무효/만료 토큰은 진입 시 로그인으로.

---

## 3. 그 외 (Infra / DevOps)

### 서비스 구성 (docker-compose)
| 서비스 | 역할 |
|---|---|
| `fastapi_backend` :8000 | 백엔드 API |
| `nextjs_frontend` :3000 | 프론트(로컬/터널용) |
| `pgvector` :5432 | PostgreSQL + pgvector |
| `redis` :6379 | 캐시·큐 |
| `graph_db` :7474/7687 | Neo4j |
| `pgadmin` :5050 | DB 조회 UI |
| `n8n` :5678 | 워크플로 자동화(메시징) |
| `korean_law_mcp` :3100 | 한국 법령 MCP 서버 |
| `cloudflared` | 터널 (백엔드 공개: `api.foodopenlab.com`) |

### 배포
- **프론트**: Vercel, Root Directory = `frontend`, `main` 브랜치 빌드 → `foodopenlab.com`.
  - `outputFileTracingRoot`는 **설정 금지**(Vercel 모노레포 트레이싱과 충돌해 빌드 실패).
  - `BACKEND_URL` = `https://api.foodopenlab.com` (Vercel env).
- **백엔드**: 서버(Ubuntu) Docker + Cloudflare Tunnel로 공개.

### PKS (Project Knowledge System)
- 문서 우선순위: `CLAUDE.md`(마스터) > 하위 `CLAUDE.md` > `_docs/` 스택 규약.
- 변경 시 버전 로그 필수: `backend/_docs/backend_ver_log.md`, `frontend/_docs/frontend_ver_log.md`.

---

## 4. 대표 데이터 흐름

**시맨틱 챗봇**: 프론트 `/api/gateway/ask` → EXAONE 의도분류 → RAG(bge-m3+pgvector+EXAONE) / 법령검색 / Gemini / 차단 → 감사로그(`gateway_audit_logs`).

**크롤러·스크래퍼(스카우트)**: 어드민이 URL+자연어 명령 입력 → Gemini 해석 → 크롤/스크랩 실행.
- 입력 이력 → **Redis**(`ontology:scout:requests`)
- 결과물 → **파일**(`backend/apps/ontology/resources/{crawled,scraped}/*.jsonl`)
- 조회 → 어드민 "수집 결과" 페이지(`/admin/scout/results`) → 사용자가 필터링 후 Redis 적재.
