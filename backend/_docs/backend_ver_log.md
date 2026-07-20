# Backend Version Log

## [v0.2.9] - 2026-07-20

### Removed
- **고아가 된 화이트리스트 HTTP 라우터 제거** — 회원 관리(`/admin/members` 승격/강등)로 대체되어 더 이상 어떤 UI도 호출하지 않는 `whitelist_router.py`(`POST/GET/DELETE /admin/whitelist`)와 전용 스키마 `whitelist_schema.py`(`AddWhitelistRequest`/`WhitelistResponse`) 삭제. `v1/__init__.py`의 라우터 등록·`schemas/__init__.py`의 export도 정리.
- **유지**: `whitelist_use_case`·`whitelist_interactor`·`whitelist_repository`·`whitelist_pg_repository`·`whitelist_dto`·`dependencies/whitelist`·`expert_whitelist_orm` — 회원 승격/강등(`member_interactor`)이 use case로 재사용하므로 그대로 둠.

### Notes
- 검증: 재시작 후 `GET /admin/whitelist` → **404**, `GET /admin/members` → **200**. 승격/강등 경로 이상 없음.
- 트레이드오프: 가입하지 않은 이메일을 미리 화이트리스트에 넣는(HTTP) 기능은 사라짐. 승격은 이제 "가입한 회원"에 대해서만 가능(`member_interactor`). 필요 시 라우터 복구 가능.

## [v0.2.8] - 2026-07-20

### Changed
- **화이트리스트를 가입 게이트 → 관리자 승격 방식으로 개편.** 이메일 회원가입에서 화이트리스트 사전 승인 검사 제거(`auth_interactor.signup`) — 누구나 가입 가능. 역할은 더 이상 하드코딩("expert")하지 않고 **화이트리스트 승격 여부로 결정**(`_resolve_role`: 화이트리스트에 있으면 `expert`, 없으면 `general`)하며 signup·login·refresh·소셜(OAuth) 전 경로에 일관 적용. 소셜 유저도 `oauth_user_pg_repository`에서 화이트리스트로 role 결정(기존 general 하드코딩 제거).
- `SignupResponse.role` 리터럴을 `Literal["expert"]` → `Literal["expert","general"]`로 확장(`auth_schema`) — 일반회원 가입 응답이 검증 실패하던 문제 해결.

### Added
- **어드민 회원 관리 슬라이스**(`apps/mfds_admin`, `verify_admin_token` 보호):
  - `GET /admin/members` — 가입 회원 전체를 승격 여부(`is_expert`)·가입경로·가입일·마지막로그인과 함께 반환(`expert_users` LEFT JOIN `expert_whitelist`).
  - `POST /admin/members/{email}/promote` — 전문가 승격(화이트리스트 추가, 멱등).
  - `POST /admin/members/{email}/demote` — 승격 해제(화이트리스트 제거, 멱등).
  - 프랙탈 세트: `member_dto`·`member_use_case`·`member_interactor`(승격/강등은 기존 `WhitelistUseCase` 재사용)·`member_repository`·`member_pg_repository`·`member_schema`·`member_router`·`dependencies/members`. DB 마이그레이션 불필요(화이트리스트 테이블 재사용).

### Notes
- E2E 검증: 화이트리스트 없이 가입 → 201·role general → `/admin/members`에 노출(is_expert=false) → promote 204 → 재로그인 role expert → demote 204 → 재로그인 role general. 전 구간 통과.

## [v0.2.7] - 2026-07-20

### Fixed
- **Alembic 전체 실행 불능 해소** — `alembic/env.py`가 삭제된 `moneyball` 앱의 ORM(`stadium/team/schedule/player_orm`)을 상단에서 import해 `ModuleNotFoundError`로 env.py 로드 자체가 실패, 모든 alembic 명령(`current`/`upgrade`/`revision`)이 죽어 있었음. 해당 import 4줄 제거. 마이그레이션 `1e4fd7b6809c`는 moneyball을 `upgrade()` 내부에서만 import하고 이미 적용 완료(DB에 stadium/team/player 존재) → 재실행되지 않으므로 무해, 체인 보존 위해 파일 유지.
- 결과: `alembic current`·`alembic upgrade head` 정상화. v0.2.6에서 수동 `ALTER`로 넣었던 `oauth_provider_id`를 롤백 후 **마이그레이션 `20260720_01`로 정식 재적용**(1e4fd7b6809c → 20260720_01, 현재 DB head).

### Notes
- `env.py`의 `target_metadata`(Base.metadata)에 이제 moneyball 테이블이 없으므로, 향후 `alembic revision --autogenerate` 시 orphan 테이블(stadium/team/player) drop을 제안할 수 있음 — 자동생성 시 검토 필요(수동 마이그레이션엔 영향 없음). orphan 테이블·데이터 정리는 별도 판단 대상이라 손대지 않음.

## [v0.2.6] - 2026-07-20

### Added
- **소셜 OAuth 로그인/회원가입 (Google·Kakao·Naver)** — `mfds_user`에 Authorization Code 플로우 풀 구현. 흐름: `GET /auth/{provider}/login`(state 발급·Redis 저장 후 제공사 동의로 302) → `GET /auth/{provider}/callback`(state 검증 → 토큰 교환·userinfo → 유저 upsert → 우리 JWT 발급 → Redis 저장 → 프론트 `/auth/callback#access_token=…&refresh_token=…`로 복귀). 프랙탈 세트:
  - dto `oauth_dto.OAuthProfile`, input port `oauth_use_case`, interactor `oauth_interactor`(provider_factory·user_repo·session_store 주입), router `oauth_router`, DI `dependencies/oauth.py`.
  - **Provider Strategy + Factory**: `oauth/base_oauth_adapter`(공통 OAuth2 Template Method) + `google/kakao/naver_oauth_adapter`(엔드포인트·scope·프로필 파싱만 override) + `oauth_provider_factory`. 각 어댑터는 `{PREFIX}_CLIENT_ID/SECRET/REDIRECT_URI` env를 읽고, 미설정 시 400. 카카오 이메일 미제공 대비 합성 이메일 fallback.
  - **Redis 세션 스토어**: `session_store_port` + `redis_session_store_adapter` — 발급 JWT(access/refresh)를 `mfds:user:session:{access|refresh}:*`에 TTL 저장(access=JWT 만료, refresh=`USER_REFRESH_EXPIRE_DAYS` 기본 14일), 유저별 refresh 집합·OAuth state(`mfds:user:oauth:state:*`, 10분) 관리. 키 SSOT `redis/redis_keys.py`.
  - **소셜 유저 upsert**: `oauth_user_repository` + `oauth_user_pg_repository` — **전문가 화이트리스트 우회**, `expert_users`에 `auth_provider`(google/kakao/naver)로 저장, `(provider, provider_id)` 또는 이메일로 기존 계정 연결, JWT role은 미사용이던 **`general`** 발급(전문가 권한과 구분).
- `expert_users.oauth_provider_id`(String(255), index) 컬럼 + 마이그레이션 `20260720_01_expert_users_oauth_provider_id.py`(down_revision=`1e4fd7b6809c`).
- `.env`에 `GOOGLE_*`/`KAKAO_*`/`NAVER_*` (CLIENT_ID/SECRET/REDIRECT_URI)·`FRONTEND_URL`·`USER_JWT_SECRET`·`USER_REFRESH_EXPIRE_DAYS` 플레이스홀더 추가(발급값은 사용자가 채움).

### Notes
- 검증(더미 자격증명): 3사 authorize URL 생성, Redis state 1회성 소비, DB upsert 멱등, JWT role=general, Redis 세션 저장→조회→로그아웃 삭제 전 구간 통과. 실제 제공사 토큰 교환(`fetch_profile`)은 콘솔 앱 등록·실사용자 필요.
- (작업 당시) Alembic이 `env.py`의 `moneyball` import로 깨져 있어 새 컬럼을 임시로 수동 `ALTER`로 반영했음 → **v0.2.7에서 env.py 수정 후 마이그레이션 `20260720_01`로 정식 재적용 완료.**

## [v0.2.5] - 2026-07-20

### Changed
- **API 문서(`/docs`·`/redoc`·`/openapi.json`) 인증 보호** (`main.py`) — 기존엔 누구나 열람 가능했음. `FastAPI(docs_url=None, redoc_url=None, openapi_url=None)`로 기본 라우트를 끄고, HTTP Basic 게이트(`_verify_docs_credentials`, `secrets.compare_digest`)를 통과한 요청에만 노출하는 커스텀 라우트로 대체. 자격증명은 `.env`의 기존 `ADMIN_EMAIL`/`ADMIN_PASSWORD` 재사용(미설정 시 503). 미인증 시 `401 + WWW-Authenticate: Basic` → 브라우저 로그인 창.

### Fixed
- 전역 `HTTPException` 핸들러(`_http_exception_handler`)가 `exc.headers`를 버려, 401의 `WWW-Authenticate` 등 응답 헤더가 유실되던 문제 수정(`headers=exc.headers` 전달). 이 수정이 없으면 보호된 `/docs`에서 브라우저 Basic 인증 팝업이 뜨지 않음.

## [v0.2.4] - 2026-07-20

### Added
- **추론 모델 단일 어댑터** `core/matrix/grid_exaone_llm_manager.py` — 임베딩 전용 `grid_embedding_manager`(bge-m3)와 대칭 구조로, 로컬 Ollama EXAONE 추론의 전역 SSOT. `LLM_MODEL`(`EXAONE_MODEL` env, 기본 `exaone3.5:7.8b`)·`OLLAMA_HOST` 상수와 `chat_sync`/`chat`(async, `to_thread`) 제공(`format`·`options` 위임). 모델 문자열·Ollama 클라이언트를 앱마다 하드코딩하지 않으므로 추론 모델이 섞일 수 없음.

### Changed
- 6개 추론 호출부를 매니저 경유로 통일 — `mfds_user`(`ollama_adapter`, `regulation_chat_interactor`의 langchain `ChatOllama`는 `LLM_MODEL`/`OLLAMA_HOST` 상수만 소싱)·`braindead`(`llm_gateway`, httpx 직접 호출 제거)·`ontology`(`law_rag_adapter`·`exaone_intent_classifier_adapter`)·`core/lol`(`v1_mid_faker_orchestrator`)·`titanic`(`crew_andrews_architect_repository`). 각 파일의 개별 `ollama.Client`·모델 fallback 문자열 제거.

### Fixed
- 추론 모델 fallback 불일치 정리 — 흩어져 있던 `exaone3.5:2.4b`(4곳)·`anpigon/eeve-korean-10.8b`(titanic)를 단일 `exaone3.5:7.8b`로 통일. env 미설정 시 `core/lol`·`titanic`이 각각 2.4b·eeve로 갈라지던 문제 해소.

### Removed
- 분산 env 변수 `BRAINDEAD_MODEL`·`OLLAMA_MODEL_LOL`·(titanic)`OLLAMA_MODEL` 및 `.env`의 `BRAINDEAD_MODEL` 항목 — 추론 모델 지정은 `EXAONE_MODEL` 하나로 단일화. `FakerOrchestrator`의 per-instance `model` 오버라이드 인자 제거(모델 혼입 차단).

## [v0.2.3] - 2026-07-16

### Added
- **스카우트 결과 조회 엔드포인트** `GET /api/scout/results?kind=crawled|scraped&limit=200`(어드민 전용, `verify_admin_jwt`) — resources JSONL(`crawled.jsonl`/`scraped.jsonl`)을 읽어 최신순 행으로 반환. 프랙탈 세트: dto(`ScoutResultsView`)·input port(`scout_results_use_case`)·interactor(`scout_results_interactor`, kind 화이트리스트 검증·limit 1~1000 클램프)·output port(`scout_result_reader_port`)·adapter(`file_scout_result_reader_adapter`, JSONL 파싱·역순)·schema(`ScoutResultsResponse`)·router 엔드포인트·DI(`scout_provider`). 잘못된 kind는 400.

## [v0.2.2] - 2026-07-16

### Added
- **스카우트 입력 이력 Redis 저장** — 어드민이 입력한 URL·자연어 명령·해석 계획을 실행 시 Redis LIST(`ontology:scout:requests`, 최근 500개 유지)에 JSON으로 기록. `IScoutRequestSinkPort` + `RedisScoutRequestSinkAdapter`(RPUSH+LTRIM) 신설, `scout_interactor`가 해석 직후(실행 전) 기록, `scout_provider`·`redis_keys`에 배선.
- **크롤러 결과 resources 파일 저장** — 크롤러가 찾은 관련 페이지(`CrawlFinding`: url·title·matched_keywords)를 `apps/ontology/resources/crawled/crawled.jsonl`에 JSONL append. `ICrawlSinkPort` + `FileCrawlSinkAdapter` 신설, `crawler_interactor`가 항상 저장(`CrawlReport.findings_saved` 추가), `crawler_provider`에 배선. 사용자가 직접 확인·필터링 후 Redis에 적재하는 원천 파일.

### Changed
- `CrawlRequest.enqueue_to_scraper`(기본 True) 추가 — 크롤러의 스크래퍼 큐 자동 적재를 옵션화. 스카우트 경로는 `False`로 꺼서(필터링 전 Redis 유입 차단) resources 저장만 하고, 기존 `/crawler/run`은 자동 적재 유지(하위 호환). 키워드 판정은 `any_match` → `matches`(매칭 키워드까지 수집)로 대체하되 동치(빈 키워드=전체 관련).

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
