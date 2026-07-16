# Backend Version Log

## [v0.2.1] - 2026-07-16

### Added
- `apps/ontology`에 **스카우트 오케스트레이터** 추가 — 어드민이 입력한 시드 URL·자연어 명령을 받아 실행하는 단일 진입점 `POST /api/scout/run`(어드민 전용, `core/matrix/grid_admin_guard_manager.verify_admin_jwt`로 보호). 프랙탈 세트: dto(`scout_dto`의 `ScoutCommand`/`ScoutPlan`/`ScoutResult`)·input port(`scout_use_case`)·interactor(`scout_interactor`, 모드 분기는 조건문 대신 dispatch table)·output port(`command_interpreter_port`)·adapter(`gemini_command_interpreter_adapter`, 게이트웨이와 동일한 `IGeminiPort`로 자연어→JSON 파라미터 해석·클램핑)·schema(`scout_schema`)·router(`scout_router`, `/myself` 배선검증 포함)·DI(`scout_provider`, `get_gemini_port`·`get_crawler_use_case`·`get_scraper_use_case` 재사용). 흐름: 명령 해석 → 모드별(crawler/scraper) 기존 use case 실행 → 계획+결과 요약 반환. LLM 파싱 실패 시 예외 대신 안전한 기본값 계획으로 폴백.

### Changed
- `crawler`/`scraper` 요청 DTO에 옵션 필드 추가 — `CrawlRequest.seed`·`CrawlRequest.keywords`, `ScrapeRequest.url`·`ScrapeRequest.keywords`. 주어지면 Redis 소스(`next_seed`/`load_keywords`) 대신 요청값을 사용(스카우트가 입력 URL을 시드/대상으로 주입하기 위함). 인터랙터는 요청값 우선, 없으면 기존 Redis 경로 유지 — 기존 `/crawler/run`·`/scraper/run` 계약은 하위 호환. 스크래퍼는 `url`이 오면 큐에 먼저 적재 후 소비.

## [v0.2.0] - 2026-07-15

### Added
- `apps/ontology`에 **시맨틱 게이트웨이**(Hub) 추가 — 챗봇 단일 진입점 `POST /api/gateway/ask`. 질문을 EXAONE(`exaone3.5:2.4b`)로 JSON 4-way 분류(`search`/`rag`/`general`/`reject`) 후 목적지별 위임. 프랙탈 세트: dto+enum(`gateway_dto`의 `Destination`/`Intent`/`GatewayQuery`/`GatewayResult`)·input port(`gateway_use_case`)·interactor(`gateway_interactor`, 조건문 대신 dispatch table)·output ports(`intent_classifier_port`/`rag_port`/`search_port`/`gemini_port`/`audit_log_port`)·adapters(`exaone_intent_classifier_adapter` `format=json`, `gemini_adapter`, `law_rag_adapter`, `law_search_adapter`)·router(`gateway_router`, `/myself` 배선검증 포함)·DI(`gateway_provider`). 분기: `general`→Gemini, `rag`→EXAONE+law_chunks RAG, `search`→law_chunks 키워드 조회, `reject`→고정 차단응답.
- `rag`/`search`는 Hub→Spoke 재사용 — `law_rag_adapter`가 `mfds_user`의 `embed_text`(bge-m3)+`LawChunkPgRepository`(pgvector top-6, `source_types=("law","admrul")`)로 조문 검색 후 EXAONE가 근거 답변 생성, `law_search_adapter`가 `LawChunkORM` ILIKE 키워드 조회(생성 없이 목록).
- **감사 로그 테이블** `gateway_audit_logs`(ontology 첫 DB 테이블) — entity(`gateway_audit_log_entity`)·orm(`gateway_audit_log_orm`, `question`/`destination`/`entities` JSONB/`blocked`/`answer_preview`/`client_ip`/`latency_ms`)·port(`audit_log_port`)·repository(`gateway_audit_log_repository`). 모든 요청·분류결과를 append(로그 실패는 응답을 막지 않음). `create_ontology_tables`(`db_init`) 신설 + `main.py` lifespan 등록, ORM은 `outbound/orm/__init__.py`에 등록. pgAdmin으로 모니터링.
- **Rate limit** — `core/matrix/grid_redis_manager.py`(Redis async 싱글톤) 추가, `ontology/dependencies/rate_limit.py`(IP당 분당 30회 fixed window, `GATEWAY_RATE_LIMIT_PER_MIN`, Redis 장애 시 fail-open)를 `gateway_router`에 LLM 분류 이전 게이트로 적용. 초과 시 429. E2E: 카운터 프리셋 후 31번째 429 확인.
- 개발용 **pgAdmin** 서비스(`docker-compose.yaml`, `dpage/pgadmin4` :5050, `docker/pgadmin/servers.json`로 pgvector 자동 등록) — pgvector DB 조회·모니터링. 문서 `apps/mfds_user/_docs/pgadmin.md`.
- 의존성 추가(`requirements.txt`): `google-genai==2.11.0`(keymaker의 Gemini 클라이언트가 전제하나 미설치였음 — 리포트·피드백 등 기존 Gemini 기능도 함께 복구), `redis==8.0.1`.

### Changed
- Gemini 모델을 `gemini-3.5-flash` 단일 구성으로 변경(`grid_keymaker_secret_manager`의 `DEFAULT_GEMINI_MODEL`·`FALLBACK_GEMINI_MODELS`) — 하위 폴백 모델(2.5-flash/lite) 제거. 모든 Gemini 호출(게이트웨이 general + 일일 리포트 + 피드백 분석)에 일괄 적용. 무료 티어 15 RPM/1M TPM/1,500 RPD.
- `ontology/gemini_adapter`를 graceful하게 — 미연결·호출 실패 시 예외 대신 안내 문구 반환(게이트웨이 general이 500 대신 응답+로그 유지).

### Fixed
- `backend/.env`의 `REDIS_URL` 오염 수정 — `redis://redis:6379/0WEATHER_API_KEY=...`처럼 줄바꿈 누락으로 `WEATHER_API_KEY`가 값에 붙어 있어 Redis 연결과 날씨·식중독 위험등급 기능(`risk_and_llm_adapters`, `main.py` 날씨 엔드포인트)이 깨져 있던 것을 두 줄로 분리해 복구.

### Removed
- `mfds_user`의 `GeminiAdapter`(`LlmPort` 구현) 삭제 — 어디에도 배선되지 않은 dead code. 챗봇 LLM은 `OllamaAdapter`(EXAONE)로 고정, Gemini는 keymaker 경유만 사용하는 결정에 따름.
- `ontology`의 Gemini 직접 엔드포인트 제거(`gemini_router`/`gemini_schema`/`gemini_provider`/`gemini_interactor`/`gemini_use_case`/`gemini_dto`) — 게이트웨이를 우회해 rate limit·분류·감사로그를 건너뛰는 뒷문 차단. `gemini_adapter`/`gemini_port`는 게이트웨이 general 경로가 재사용하므로 유지.

## [v0.1.17] - 2026-07-15

### Added
- `mfds_user`에 법령 시맨틱 검색(RAG) 프랙탈 세트 추가 — `law_chunks`(krcofoodrm에서 이관한 44,518청크, bge-m3 1024차원, HNSW cosine)를 대상으로. entity(`law_chunk_entity`)·orm(`law_chunk_orm`, pgvector `Vector`)·output port(`law_chunk_repository`)·pg repository(`law_chunk_pg_repository`, `cosine_distance` top-k)·dto(`law_chunk_dto`)·input port(`law_chunk_use_case`)·interactor(`law_chunk_interactor`, `grid_embedding_manager.embed_text`로 질문 임베딩)·schema·router(`GET /law-chunk/myself` 배선검증 + `POST /law-chunk/search`)·DI(`dependencies/law_chunk.py`). ORM은 `outbound/orm/__init__.py`에 등록, 라우터는 `user_router`에 편입. 매핑은 앱 관례대로 리포지토리·라우터 인라인.

### Changed
- `regulation_chat_interactor`를 하이브리드로 전환 — "최근 개정/처분/체계/절차" 키워드(`_pick_task`)는 기존 `korean_law_mcp` 실시간 조회 유지, 그 외 일반 질문은 `law_chunks` pgvector RAG로 조문 원문을 근거 제공(`_format_rag_context`/`_hits_to_refs` 추가). `dependencies/regulation_chat.py`가 `LawChunkInteractor`(+`get_db` 세션)를 주입. 시스템 프롬프트 라벨을 소스 중립적으로 수정.
- RAG 근거를 **법령 원문만**으로 제한 — 챗 검색을 `source_types=("law","admrul")`(법률·시행령·시행규칙 + 고시/행정규칙)로 좁혀 판례·결정례·유권해석·가이드·FAQ를 근거에서 제외(`_LAW_SOURCE_TYPES`). 독립 `/law-chunk/search`는 무제한 유지.
- 선택적 `source_type` 필터가 HNSW 근사 인덱스와 겹칠 때 전역 최근접 후보가 필터로 전부 걸러져 0건이 나오던 문제를, 필터 존재 시 `SET LOCAL hnsw.iterative_scan = strict_order`(pgvector 0.8) 적용으로 해소(`law_chunk_pg_repository`). E2E 검증: 필터 검색 6건(admrul), `/regulation-chat`(exaone3.5:7.8b)가 `식품 및 축산물 안전관리인증기준`(HACCP 고시)만 참조하며 시행규칙 제62조·별표 18 인용(29s).
- 로컬 Ollama LLM 모델을 `exaone3.5:2.4b` → `exaone3.5:7.8b`로 변경(`backend/.env` `EXAONE_MODEL`·`BRAINDEAD_MODEL`) — 이전 PC에 2.4b 미설치, 설치된 7.8b에 맞춤.

## [v0.1.16] - 2026-07-15

### Changed
- 개발+운영 머신을 새 Windows PC(`kimchungs`, i5-12400F / 32GB / RTX 3060 Ti 8GB)로 이전 완료. 깨진 git 인덱스 복구(`git reset`), DB 볼륨 5개(`comfoodopenlab_pgvector_data`·`_neo4j_data`·`_neo4j_logs`·`_redis_data`·`n8n_data`) `foodopenlab_db_backup/`에서 복원, `docker compose up -d`로 8개 서비스 정상 기동 확인(backend/frontend 200, pgvector 35 테이블, GPU 패스스루 작동). 우분투 서버 이전 계획은 폐기.

### Removed
- `docs/server_move.md` — Windows→Ubuntu 이전 절차 문서. 실제로는 Windows→Windows 이전이라 불필요해져 삭제(이전 완료 기록은 위 v0.1.16 로그로 대체).

## [v0.1.15] - 2026-07-14

### Added
- `apps/moneyball`에 축구 ERD 4개 테이블 ORM 추가 — `stadium`/`team`/`schedule`/`player` (`adapter/outbound/orm/*_orm.py`). 각 테이블에 pgvector 시맨틱 검색용 임베딩 컬럼(`stadium_embedding`/`team_strategy_embedding`/`match_summary_embedding`/`player_profile_embedding`)을 `Vector(EMBEDDING_DIM)` = 1024차원(로컬 bge-m3)으로 정의. `soccer-database.md` 명세의 1536(OpenAI)이 아닌, 프로젝트 실제 임베딩 파이프라인(`grid_embedding_manager`)과 일치하도록 1024 채택. FK(team→stadium, schedule→stadium, player→team), `schedule` 복합 PK(`sche_date`,`stadium_id`), ERD 원본 오타 `statdium_name` 유지.
- Alembic 마이그레이션 `1e4fd7b6809c` 추가 — `CREATE EXTENSION IF NOT EXISTS vector` 후 4개 테이블 생성(`Base.metadata.create_all`, checkfirst). 기존 DB는 alembic 미스탬프 상태였어 `alembic stamp head`로 정합화 후 신규 리비전만 적용. 검증: 익스텐션(0.8.3)·4개 테이블·1024차원 벡터 INSERT(dim=1024)·FK 거부·복합 PK 동작 확인.

### Changed
- `alembic/env.py`에 moneyball ORM 4개 import 등록(메타데이터 편입).

## [v0.1.14] - 2026-07-14

### Added
- `core/matrix/grid_device_manager.py` 추가 — `resolve_device()`가 torch 추론 디바이스를 자동 선택(우선순위: 인자 > `TORCH_DEVICE` 환경변수 > CUDA 감지). CUDA GPU가 있으면 `"cuda"`, 없으면 `"cpu"`. apps/ 전역 공유 인프라(허브).

### Changed
- `apps/ontology`의 얼굴 인식 HTTP 추론 엔드포인트(`vision_router.py`)가 `device="cpu"` 하드코딩 대신 `resolve_device()`를 사용 — GPU가 있으면 자동으로 GPU 추론. CLI(`face_recognition_cli.py`)는 이미 `--device 0`(GPU) 기본값이라 무변경.

## [v0.1.13] - 2026-07-13

### Changed
- `apps/vision` Bounded Context를 허브 `apps/ontology`로 통합하고 `apps/vision` 폴더 삭제. vision의 `adapter·app·dependencies·domain·resources·tests`를 `ontology/` 하위로 이동하고, 이동된 모든 파일과 `main.py`의 import 접두어를 `vision.` → `ontology.`로 치환(파일명·심볼명 `vision_*`/`face_recognition_*`는 유지). vision CLI docstring의 예시 경로도 `apps/vision/` → `apps/ontology/`로 수정. 기존 `ontology.channel`/`ontology.classification` 어휘(`braindead`가 참조)는 그대로 유지되며 import 무영향. 라우터 체인(`ontology.adapter.inbound.api.vision_router`) import 검증 및 하네스 토폴로지 검증(고립·허브 순환) 통과.

- `apps/ontology`의 비프랙탈 최상위 어휘 폴더 `channel/`·`classification/`(순수 `str, Enum` Value Object)을 프랙탈 정위치인 `domain/value_objects/` 아래로 이동(분류 그룹 유지). 이에 따라 `braindead`의 `MessageCategory` import 6곳을 `ontology.classification.message_category` → `ontology.domain.value_objects.classification.message_category`로 갱신. 이동 후 `ontology` 최상위는 순수 헥사고날 프랙탈 구조(adapter/app/dependencies/domain/tests/resources)만 남음. VO import·braindead 체인 검증 및 하네스 고립 노드 검증 통과.
- `apps/ontology/_docs/star-craft-pipeline.md`를 실제 허브 패키지 `ontology` 기준으로 정합화: frontmatter `domain: star_craft` → `ontology`(하네스 hub 검증 INVALID 해소), 위치 경로 `backend/apps/star_craft/` → `backend/apps/ontology/`, 예제 import 경로·DI `star_craft.*` → `ontology.*`, Qdrant 컬렉션 `star_craft_global` → `ontology_global`, 다이어그램 식별자 `StarCraftUseCase` → `OntologyUseCase`, 예제 라우트 `/api/star-craft/context` → `/api/ontology/context`. 코드네임 테마 제목 "Star Craft Hub"는 유지.

### Removed
- `apps/vision/` 디렉토리 (내용 전부 `apps/ontology/`로 이관).

## [v0.1.12] - 2026-07-09

### Changed
- CORS `allow_origins`를 하드코딩(localhost 전용)에서 `CORS_ORIGINS` 환경변수 기반으로 변경(`main.py`). 기본 로컬 오리진에 env로 지정한 운영 도메인을 더해 허용한다. Vercel 프론트(`https://foodopenlab.com`)가 Cloudflare 백엔드(`https://api.foodopenlab.com`)를 호출할 때 CORS 차단되던 문제 해결. 도메인 변경 시 이미지 재빌드 없이 `.env`만 수정하면 됨.

## [v0.1.11] - 2026-07-03

### Added
- `apps/vision`에 이미지 업로드 기능 추가: `POST /api/vision/images` (multipart `file` 필드). `vision_interactor.py`가 확장자 화이트리스트(`.png .jpg .jpeg .gif .webp .bmp`)를 검증(위반 시 400)하고, `vision_repository.py`가 `backend/data/vision_uploads/`에 UUID 파일명으로 저장. Hexagonal 레이어(schema/dto/input-port/output-port/interactor/repository) 전부에 `upload_image`/`save_image` 추가.

## [v0.1.10] - 2026-07-03

### Added
- `apps/vision/` 신규 Bounded Context 스켈레톤 추가 (`watcher`/`judge`와 동일한 8-file fractal set: schema/router/dto/use_case/port/interactor/repository/provider). 아직 실제 도메인 기능·DB 테이블은 없고 `GET /api/vision/myself`로 router→use_case→interactor→port→repository 전체 배선만 검증된 상태 — CLAUDE.md `myself` 엔드포인트 규칙 적용 사례. `main.py`에 `vision_router` 등록.

## [v0.1.9] - 2026-07-03

### Changed
- `POST /auth/signup` 응답(`SignupResponse`)에 `access_token`/`token_type` 추가. 인터랙터(`auth_interactor.py`)는 가입 시점에 이미 세션을 발급하고 있었으나 라우터가 토큰을 응답에 실지 않아, 가입 직후 전문가 회원이 별도로 `/login`을 다시 거쳐야만 마이페이지 기능(업종/관심 설정 등)을 쓸 수 있었던 문제를 해결 — 가입 즉시 자동 로그인 가능하도록 계약 확장.

## [v0.1.8] - 2026-07-02

### Added
- `braindead` 앱에 `watcher`, `judge` 도메인 스켈레톤(각 8-file fractal set: router/schema/dto/use_case/port/interactor/repository/provider) 추가. 아직 실제 기능은 없고 `GET /watcher/myself`, `GET /judge/myself`로 router→use_case→interactor→port→repository 전체 배선만 검증된 상태 — CLAUDE.md `myself` 엔드포인트 규칙 적용 사례.

## [v0.1.7] - 2026-07-02

### Fixed
- `regulation-chat`이 관련 법령을 못 찾았을 때(MCP 툴이 `isError=True` + `[NOT_FOUND]...` 반환) `korean_law_mcp_adapter.py`가 이 신호를 무시하고 해당 텍스트를 그대로 LLM 컨텍스트에 밀어 넣던 버그. 시스템 프롬프트에 "추측하지 마세요"라고 적혀 있어도 로컬 2.4B 모델(`exaone3.5:2.4b`)이 이를 안정적으로 못 지켜 존재하지 않는 법령 조문을 지어내는 원인이었음.
- `research_law()`/`search_laws()`가 미발견 시 `None`/빈 리스트를 명확히 반환하도록 수정하고, `regulation_chat_interactor.py`는 이 경우 **LLM을 호출하지 않고** 코드로 확정적으로 안전 문구("확인이 필요합니다 — law.go.kr에서 직접 확인을 권장합니다")를 반환하도록 변경 — 프롬프트 신뢰 대신 코드로 환각을 원천 차단.

## [v0.1.6] - 2026-07-02

### Added
- `braindead_inbox` 테이블에 pgvector `embedding` 컬럼(1024차원) 추가 — 이메일 수신 시 `core/matrix/grid_embedding_manager.py`(로컬 Ollama `bge-m3` 모델)로 본문 임베딩을 자동 생성·저장.
- `requirements.txt`에 `pgvector==0.4.2` 추가. `db_init.py`에 `CREATE EXTENSION IF NOT EXISTS vector` + 기존 테이블 보강용 `ALTER TABLE braindead_inbox ADD COLUMN IF NOT EXISTS embedding vector(1024)` 추가(무손실 마이그레이션).

### Changed
- `Dockerfile`을 heavy(`requirements-heavy.txt`: torch/langchain/neo4j/qdrant 등 무거운 의존성)/light(`requirements.txt`) 2단계 레이어 + BuildKit `--mount=type=cache` pip 캐시 마운트로 분리 — 이후 가벼운 의존성만 바뀌어도 무거운 레이어는 캐시로 재사용되어 재빌드 시간·트래픽 대폭 절감.

## [v0.1.5] - 2026-07-02

### Added
- `mfds_user`에 `food_poisoning_stat` 신규 도메인(Fractal set) 추가 — 식중독 통계(식품안전나라 오픈API 원인물질별 I2850 / 원인시설별 I2849)를 `food_poisoning_stat_cache` 테이블에 적재. `GET /food-stats/yearly`, `/food-stats/by-agent`, `/food-stats/by-facility` 3개 엔드포인트 신규.
- 기존 `recall_scheduler.py`의 09:40/17:40 staggered wave에 식중독 통계 동기화 스텝 추가(신규 시간대 없이 재사용). 최초 배포 시 테이블이 비어있으면 즉시 1회 백필하는 `ensure_food_poisoning_stat_db_cache_on_startup()` 추가.

### Fixed
- 프론트가 그동안 호출하던 `apis.data.go.kr/FoodPoisStat`는 애초에 활용 승인이 안 된 잘못된 API였음(항상 HTTP 500). 같은 식품안전나라 오픈API 플랫폼(recall과 동일 플랫폼, 기존 `FOOD_SAFETY_API_KEY` 재사용)의 올바른 서비스ID(I2850/I2849)로 교체.

## [v0.1.4] - 2026-07-01

### Added
- `mfds_user`에 `/admin/data-sync/status`(GET), `/admin/data-sync/trigger`(POST) 엔드포인트 신규 추가 — 이전엔 프론트 `/admin/data-sync` 페이지가 호출하는 API가 아예 없어서(404) 화면이 항상 실패 상태였음.
- `status` 응답에 `last_sync_at`/`sync_wave`/`sync_slot`(기존 `food_safety_sync_state.py`가 이미 기록해두고 있었지만 어디서도 노출되지 않던 값) 추가.
- `core/matrix/grid_admin_guard_manager.py`의 경량 admin JWT 가드 재사용(mfds_admin 직접 참조 없이 인증 적용).

## [v0.1.3] - 2026-07-01

### Added
- `core/matrix/grid_admin_guard_manager.py` — 경량 Admin JWT 검증(`verify_admin_jwt`, 서명·만료·role만 확인, DB 재조회 없음). `mfds_admin`을 `braindead`가 직접 import하지 않도록 core로 분리.

### Changed
- `braindead` 앱의 `send-email`, `send-telegram`, `send-discord`, `contacts`(업로드/검색/목록), `inbox` 목록 조회 라우터에 Admin 인증 적용 — 로그인한 관리자만 호출 가능. n8n이 호출하는 `inbox/receive` 웹훅은 기존 시크릿 방식 그대로 유지(대상 아님).

## [v0.1.2] - 2026-07-01

### Added
- `braindead` 앱에 `inbox` 도메인(Fractal 11-File Set) 추가 — n8n Gmail Trigger가 새 수신 메일을 웹훅으로 전달하면 `POST /braindead/inbox/receive`가 DB(`braindead_inbox`)에 저장, `GET /braindead/inbox`로 목록 조회.
- `gmail_message_id` 기준 중복 저장 방지(같은 메일 재전송 시 기존 레코드 반환).
- 웹훅 인증: `N8N_INBOX_WEBHOOK_SECRET` 설정 시 `X-Webhook-Secret` 헤더 검증(미설정 시 경고 로그와 함께 허용).

## [v0.1.1] - 2026-06-30

### Fixed
- `EmailInteractor`: 이메일 제목이 사용자 프롬프트 원문으로 설정되던 버그 수정 — 이제 LLM이 본문을 생성한 후 본문 기반으로 제목을 별도 생성함
