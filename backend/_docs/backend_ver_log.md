# Backend Version Log

## [v0.4.1] - 2026-07-21

### Added
- **보안 응답 헤더 미들웨어**(`main.py`, CORS 뒤 `@app.middleware("http")`) — 전 응답에 `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`(클릭재킹), `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy: camera=(), microphone=(), geolocation=()`, `Strict-Transport-Security: max-age=31536000; includeSubDomains` 부여.
  - **CSP 경로별 분기**: 순수 JSON API는 강하게 `default-src 'none'; frame-ancestors 'none'; base-uri 'none'`; `/docs`·`/redoc`(Swagger/ReDoc)는 CDN(jsdelivr)·인라인 스크립트가 필요해 완화(`script-src/style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net` 등)해 문서가 깨지지 않게 함.

### Changed
- **`Server: uvicorn` 헤더 노출 제거** — `backend/Dockerfile` CMD에 `--no-server-header` 추가(적용에는 백엔드 **재빌드** 필요). 미들웨어에서 Server를 덮어쓰려던 무효 라인 제거.

### Notes
- 검증: 재시작 후 라이브 — `GET /` CSP=`default-src 'none'`+5헤더, `GET /docs` CSP=완화(swagger 정상), HSTS 적용 확인.
- 후속: `Server` 헤더 제거는 `docker compose up -d --build backend` 재빌드 시 반영(현재는 restart만 반영돼 헤더는 적용, Server는 잔존).

## [v0.4.0] - 2026-07-21

### Added
- **어드민 로그인·`/docs` 보호를 구글 OAuth(RBAC)로 전환.** 허용 계정은 `.env ADMIN_GOOGLE_EMAILS`(콤마 목록)로 관리, 일반사용자↔어드민은 `role=admin` 클레임으로 RBAC 구분.
  - **공유 커널 구글 헬퍼** `core/matrix/grid_google_oauth_manager.py` — `build_authorize_url(redirect_uri, state)` + `fetch_google_identity(code, redirect_uri) -> (email, name)`. redirect_uri를 호출자가 주입해 유저/어드민이 서로 다른 콜백 사용(기존 유저 구글 로그인 흐름은 무변경).
  - **어드민 구글 흐름**(mfds_admin): `GET /admin/auth/google/login`(state 쿠키 심고 구글로) + `GET /admin/auth/google/callback`(state 검증 → 이메일 → 허용목록 확인 → `AdminORM` upsert → `create_admin_token`으로 role=admin JWT 발급). `next=/docs`면 `admin_docs_session` 쿠키 설정 후 `/docs`로, 아니면 어드민 프론트 `#access_token`으로. 신규: `admin_google_auth_use_case`·`admin_google_auth_interactor`·`admin_google_auth_router`·`dependencies/admin_google_auth`, `AdminRepositoryPort.upsert_google_admin`(사용불가 랜덤 해시로 NOT NULL 충족 — 비번 로그인 폐지).
  - **core RBAC 가드 확장** `grid_admin_guard_manager.decode_admin_jwt(token)` — 헤더용 `verify_admin_jwt`와 `/docs` 쿠키 검증이 공유.
  - **`/docs`·`/redoc`·`/openapi.json`**(main.py): HTTP Basic(ADMIN_EMAIL/PASSWORD) 폐지 → `admin_docs_session` 쿠키(admin JWT, role=admin) 검증. 미인증 시 `/admin/auth/google/login?next=/docs`로 307.

### Removed
- **비밀번호 어드민 로그인 폐지**: `POST /admin/login`·`/admin/loginn`(admin_auth_router 언마운트). `admin_auth_interactor.create_admin_token`은 구글 인터랙터가 재사용하므로 존치.

### Fixed
- `seed_admin.py`가 v0.3.3에서 삭제된 `mfds_user.app.services.security`를 import하던 회귀 → `matrix.grid_cypher_password_manager`로 교정.

### Notes
- **운영 필수 조치**: ① 구글 클라우드 콘솔에 승인된 리다이렉트 URI `https://api.foodopenlab.com/admin/auth/google/callback` 추가. ② `.env`에 `ADMIN_GOOGLE_EMAILS=kcs8815@gmail.com`·`ADMIN_GOOGLE_REDIRECT_URI=...callback` 추가 완료(비밀값 아님). 기존 `ADMIN_EMAIL`/`ADMIN_PASSWORD`는 더 이상 로그인·docs에 쓰이지 않음(시드 스크립트에만 잔존).
- 검증: 재시작 후 라이브 — `GET /docs`→307(구글 로그인), `/admin/auth/google/login`→302(구글, redirect_uri·state 정상), `/admin/members` 무토큰→401(RBAC), `POST /admin/login`→404. 실제 구글 동의→콜백은 브라우저+등록된 redirect URI 필요.

## [v0.3.9] - 2026-07-21

### Changed
- **`mfds_user ↔ mfds_admin` Spoke↔Spoke 결합 해소 — 공유 커널(core) 도입.** 두 BC가 같은 물리 DB 테이블을 공유 ORM 클래스로 직접 참조하던(폴리모픽 `users` 상속 + 서로의 테이블 교차 조회) 구조를 정리.
  - **신규 공유 커널 `core/matrix/orm/`** — BC 경계를 넘어 공유되는 5개 ORM을 이관(`git mv`): `user_orm`(UserORM base, `users`)·`expert_user_orm`·`agent_message_orm`(mfds_user 소유, admin이 조회)·`expert_whitelist_orm`·`search_log_orm`(mfds_admin 소유, user가 조회). `AdminORM`·`ExpertUserORM`은 이제 `matrix.orm.user_orm.UserORM`을 상속. import 경로를 `mfds_user/mfds_admin.adapter.outbound.orm.*` → `matrix.orm.*`로 일괄 재작성(13파일). 메타데이터는 단일 `Base` 공유라 등록 무영향.
  - **인증 결합 제거**: user 라우터 2개(`daily_report_router`·`report_feedback_router`)가 `mfds_admin`의 `verify_admin_token`(+`AdminTokenPayloadSchema`)로 admin 게이팅하던 것을, 이미 존재하던 **core 가드 `matrix.grid_admin_guard_manager.verify_admin_jwt`**로 교체(서명·만료·role 검증, DB 접근 없음 — apps 간 참조 방지). 해당 게이트 파라미터는 본문 미사용이라 `_admin: str` 게이트로 정리.

### Notes
- 검증: `mfds_admin→mfds_user`·`mfds_user→mfds_admin`·`core→apps` 참조 **전부 0건**. 컨테이너 재시작 후 라이브 부팅 정상(ImportError/Traceback 없음, 스케줄러 기동), 상속·6개 테이블 등록(`users·expert_users·admins·expert_whitelist·agent_messages·search_logs`) 확인. 라이브 HTTP: `GET /`·`/recalls/latest`=200, 무토큰 `POST /admin/reports/generate`·`GET /mypage/profile`=401(가드 동작).
- `mfds_admin`의 `verify_admin_token` 미들웨어는 admin 자체 라우터용으로 존치(더 이상 user가 참조하지 않음).
- **감사에서 도출된 모든 규칙 위반 정리 완료** — Star Topology(Spoke↔Spoke 0), 레이어 경계(interactor FastAPI/ORM/adapter 침투 0, output port ORM 노출 0), Schema=DTO 혼용 0, DDD 공백(mfds_admin·siliconvalley 엔티티) 해소, 문서 SSOT 정합.

## [v0.3.8] - 2026-07-21

### Added
- **`siliconvalley` 도메인 레이어 신설 — DDD 공백(도메인 엔티티 0개) 해소.** 크루 5인(실리콘밸리 등장인물 에이전트)의 정체성을 도메인이 소유하도록 모델링:
  - `domain/value_objects/piper_role_vo.py` — `PiperRole` VO(CEO·COO·HR·SYS·DASH).
  - `domain/entities/piper_crew_member_entity.py` — `PiperCrewMember` 엔티티(id·name·role).
  - `domain/piper_crew_registry.py` — 크루 5인 정체성 **SSOT** 레지스트리 + `get_crew_member(role)`.

### Changed
- **크루 정체성을 라우터 하드코딩 → 도메인 SSOT로 이관.** 5개 슬라이스의 `introduce_myself`가 라우터에 하드코딩된 `{id,name}`을 `schema_to_query`로 넘기던 것을, interactor가 도메인 registry에서 `PiperCrewMember`를 해석해 Response를 구성하도록 변경. 라우터는 하드코딩 없이 `introduce_myself()` 호출 후 `response_to_schema`만 수행.

### Removed
- **echo 전용 outbound 레이어 제거(정적 도메인 데이터엔 불필요한 의식).** 입력을 그대로 되돌려주던 output port 5개(`app/ports/output/piper_*_port.py`)·repository 5개(`adapter/outbound/client/piper_*_repository.py`) 삭제, provider는 interactor만 구성(`get_*_use_case` 이름·라우터 배선 유지). assembler의 `schema_to_query` 제거(`response_to_schema`만 유지). 빈 스텁 `domain/piper_hendricks_ceo_topology.py` 삭제. `n8n_client`·`dependencies/providers.py`는 무관하여 유지.

### Notes
- 검증: 컨테이너에서 `piper_router` 조립(5 라우트) + 5개 interactor의 도메인 해석 스모크 통과(응답 id/name은 기존과 동일, 이제 도메인 SSOT 소스). siliconvalley 전체 py_compile OK, 잔여 참조 0건. 테스트 없음(스캐폴드).
- 잔여(경미): 각 슬라이스 dto의 `*Query`는 현재 미사용(향후 POST 엔드포인트용으로 존치). `app/use_case`(단수) 디렉토리 네이밍은 §12 관례(`app/use_cases`)와 다르나 이번 범위 밖.
- **감사 항목 전부 정리 완료** — 남은 백로그는 `mfds_user↔mfds_admin` 공유 ORM 테이블 결합(중대 리팩터) 1건.

## [v0.3.7] - 2026-07-21

### Changed
- **`titanic` jack·rose interactor의 adapter 직접 import 제거 — Clean/Hexagonal 경계 복원.** application(interactor)이 `adapter/outbound/orm/passenger_rose_model_strategies`(sklearn 기반 Strategy 구현체·팩토리)를 직접 import하던 위반 해소.
  - **전략 파일 이전**: `adapter/outbound/orm/passenger_rose_model_strategies.py` → `adapter/outbound/ml/survival_strategies.py`(`git mv`). `SurvivalModelStrategy` 포트 docstring이 지정한 위치이자, ORM(테이블)이 아닌 ML 어댑터임을 명확히 함.
  - **DI 주입**: `JackTrainerInteractor`·`RoseModelInteractor` 생성자에 `build_strategies`(팩토리 콜러블)와(rose는) 기본 `strategy`를 주입받도록 변경. 구상 전략을 import하는 책임은 composition root(`dependencies/*_provider.py`)로 이동 — 프로바이더가 `build_all_strategies`·`RandomForestStrategy()`를 wiring.

### Fixed
- **v0.3.5(Schema→Query) 리팩터로 깨졌던 titanic use_case 테스트 5건 수정.** `introduce_myself` 테스트가 `*Schema`를 넘기던 것을 `*Query`로 교체(jack·cal·james), james upload 테스트를 새 계약(interactor가 매핑된 엔티티 수신)에 맞게 재작성. jack을 생성하는 테스트(jack·cal)에 `build_strategies=build_all_strategies` 주입.

### Notes
- 검증: **전 앱** interactor의 `adapter.outbound` 직접 import **0건**, 구 strategies 경로 참조 0건. `apps/titanic/tests` **35 passed**(2 deselected=라이브 Ollama 통합). 컨테이너에서 프로바이더·interactor DI 구성 스모크 통과(전략 10종 로드).
- 남은 백로그: `mfds_user↔mfds_admin` 공유 ORM 테이블 결합, `siliconvalley` 도메인 엔티티 부재.

## [v0.3.6] - 2026-07-21

### Changed
- **`braindead`(watcher·judge)·`ontology`(vision)의 Schema=DTO 혼용 제거 — 백엔드 전체에서 이 위반 카테고리 소멸.** titanic과 동일 패턴(유일 Schema 사용처가 `introduce_myself`, `*Query` DTO 이미 존재, output port도 이미 Query 수신)이라 검증 스크립트로 3개 슬라이스 일괄 변환: port·interactor 시그니처 `schema: *Schema` → `query: *Query`, interactor의 `*Query(id=schema.id, name=schema.name)` → `query` 축약, 라우터 호출 `*Schema(...)` → `*Query(...)`. 라우터의 `response_model=*Schema`(출력 계약)는 유지.

### Notes
- 검증: **전 백엔드** `app/ports`·`app/use_cases`의 inbound schema import **0건 달성**. 컨테이너에서 watcher·judge·vision 라우터·인터랙터 import 스모크 통과.
- 이로써 감사 항목 중 "Schema=DTO 혼용"은 전 앱(titanic 12 + braindead 2 + ontology 1) 완전 해소. 남은 별도 카테고리: `titanic`의 `passenger_jack_trainer`·`passenger_rose_model` interactor ORM 직참, `mfds_user↔mfds_admin` 공유 ORM 결합, `siliconvalley` 도메인 엔티티 부재.

## [v0.3.5] - 2026-07-21

### Changed
- **`titanic` 12개 슬라이스의 Schema=DTO 혼용 제거 — 경계 게이트 정상화.** input port·interactor가 inbound `*Schema`(pydantic)를 use-case 타입으로 쓰던 위반을 앱 DTO로 교체. 각 슬라이스에 이미 존재하던 `*Query`/`*Response` DTO를 활용(output port는 이미 `*Query`를 받고 있었음).
  - **공통 `introduce_myself`(12슬라이스)**: port·interactor 시그니처를 `schema: *Schema` → `query: *Query`로, 라우터 호출을 `*Schema(...)` → `*Query(...)`로 교체(검증 포함 스크립트로 10개 단순 슬라이스 일괄 변환, smith·james 수작업). 라우터의 `response_model=*Schema`(출력 계약)는 유지 — 라우터는 Schema 사용 허용.
  - **`crew_smith_captain.chat`**: 신규 DTO `ChatCommand`/`ChatMessage` 추가. port·interactor를 `ChatSchema` → `ChatCommand`로 전환, 라우터가 요청 `ChatSchema`(Body) → `ChatCommand` 매핑.
  - **`crew_james_director.upload`**: 신규 DTO `UploadResult` 추가. port가 `list[FileUploadSchema] → UploadResultSchema` 대신 도메인 엔티티(`JackPassenger`/`RoseBooking`) → `UploadResult`를 다루도록 변경. Schema→Entity 매핑(`file_upload_schemas_to_upload_entities`)을 interactor→라우터(inbound adapter)로 이동.

### Notes
- 검증: `titanic`의 `app/ports`·`app/use_cases`에서 inbound schema import **0건**, 컨테이너에서 titanic 라우터 12개 + 인터랙터 전체 import 스모크 통과. 단순 슬라이스는 py_compile 통과.
- 남은 동종 패턴(별도, 소규모): `braindead`(port·interactor 각 2)·`ontology`(각 1)의 Schema=DTO 혼용. 별도 카테고리 잔여: `titanic`의 `passenger_jack_trainer`·`passenger_rose_model` interactor가 ORM 직접 import(모델 영속화), `mfds_user↔mfds_admin` 공유 ORM 결합, `siliconvalley` 도메인 엔티티 부재.

## [v0.3.4] - 2026-07-21

### Added
- **`mfds_admin` 도메인 엔티티 신설** `domain/entities/admin_entity.py`(`Admin`: id·email·name·hashed_password·last_login) — 그동안 도메인 엔티티 0개로 ORM을 도메인처럼 쓰던 DDD 공백 해소. `domain/`·`domain/entities/` 패키지도 함께 생성.

### Changed
- **output port의 ORM 노출 제거 — DIP 위반 해소(백엔드 전 앱 0건 달성).**
  - `admin_repository`(포트): `get_admin_by_email(...) -> Optional[AdminORM]` → `-> Optional[Admin]`. `admin_pg_repository`가 ORM→`Admin` 엔티티 매핑. `admin_auth_interactor`는 필드명이 동일해 무변경.
  - `whitelist_repository`(포트): `ExpertWhitelistORM` 노출 제거 → app DTO(`AddWhitelistCommand`/`WhitelistEntryDTO`)로 통화. `save(entry: ORM)` → `save(command: AddWhitelistCommand)`로 바꿔 **ORM 생성 책임을 interactor→repo(어댑터)로 이동**. `whitelist_pg_repository`가 ORM↔DTO 매핑(`_to_dto`) 담당, `delete_by_email`은 ORM 직접 조회로 정리. `whitelist_interactor`는 ORM import 제거·`replace(command, email=email)`로 정규화만 위임(조회 테이블이라 별도 도메인 엔티티는 두지 않음 — Simplicity First).

### Notes
- 검증: 전 앱 output port의 `adapter.outbound.orm` import **0건**, 컨테이너 스모크(엔티티·포트 시그니처·admin_auth·whitelist·member 재사용·DI·`/admin/login` 라우트) 통과. member 승격/강등은 입력 포트(`WhitelistUseCase`) 재사용이라 무영향.
- 남은 백로그: `titanic` Schema=DTO 혼용(interactor 12·port 12, ORM 직참 interactor 2 포함), `mfds_user↔mfds_admin` 공유 ORM 테이블 결합, `siliconvalley` 도메인 엔티티 부재.

## [v0.3.3] - 2026-07-21

### Changed
- **비밀번호 해싱/검증을 공유 커널 `core/`로 이전 — Spoke↔Spoke 결합 1건 해소.** `mfds_user/app/services/security.py`(`hash_password`·`verify_password`, PBKDF2-HMAC-SHA256)를 `core/matrix/grid_cypher_password_manager.py`로 이동(Matrix 네이밍 관례 준수). `mfds_admin/app/use_cases/admin_auth_interactor.py`의 `from mfds_user...security import verify_password` → `from matrix.grid_cypher_password_manager import verify_password`로 교체. 로컬 인증 폐지(v0.3.0) 이후 `security.py`는 이미 mfds_user 내부 사용처가 없어 원본 삭제(전역 이동).

### Notes
- 검증: 컨테이너 내 해시 왕복(hash→verify True/오답 False) 및 interactor가 core 함수를 참조함 확인. `mfds_admin → mfds_user` 중 **security 유틸 참조는 0건**으로 해소.
- **남은 결합(별도 후속)**: `mfds_user ↔ mfds_admin`는 여전히 **공유 ORM 테이블**로 얽힘 — `mfds_admin`이 `UserORM`·`ExpertUserORM`·`AgentMessageORM` 참조(`admin_orm`/`logs_pg_repository`/`member_pg_repository`), `mfds_user`가 `ExpertWhitelistORM` 참조(5파일). 이는 BC 간 영속성 모델 공유 문제로, 공유 커널 이전 또는 Hub(`ontology`) 경유가 필요한 중대 리팩터.

## [v0.3.2] - 2026-07-21

### Changed
- **`admin_auth_interactor`의 FastAPI 침투 제거 — Clean/Hexagonal 경계 복원.** application 레이어(interactor)가 `from fastapi import HTTPException`으로 HTTP 상태코드(503/401)를 직접 던지던 위반을 해소. 신규 애플리케이션 예외 `AdminConfigError`(설정 누락)·`AdminAuthError`(인증 실패)를 `mfds_admin/app/exceptions.py`에 정의하고, interactor는 이 도메인 예외를, 라우터(`admin_auth_router`)가 각각 503/503·401로 HTTP 변환하도록 배선. 기존 503/401 구분·에러 메시지·`/admin/loginn` 오타 alias 동작 모두 보존.

### Notes
- 백엔드 규칙 감사 후속 정리(가벼운 항목 우선). 검증: 전 앱 interactor의 `fastapi`/`Depends` 침투 grep 0건, 컨테이너 내 interactor·router·exceptions import 스모크 통과, `/admin/login`·`/admin/loginn` 라우트 정상 로드.
- 남은 백로그: `mfds_user↔mfds_admin` Spoke↔Spoke 결합, `titanic` Schema=DTO 혼용(12), output port의 ORM 노출(`admin_repository`/`whitelist_repository`) + `mfds_admin`/`siliconvalley` 도메인 엔티티 부재.

## [v0.3.1] - 2026-07-21

### Changed
- **`backend/_docs/CLAUDE.md`의 Star Topology 섹션을 실제 코드·master 스펙에 정합화(문서 SSOT 불일치 해소).** canonical child 스펙이 존재하지 않는 `apps/star_craft/`를 Hub로 명시하던 오류를 수정 — **Hub 앱은 `apps/ontology/`**(“Star-Craft”는 토폴로지 코드명일 뿐 앱명 아님)로 바로잡음. 다이어그램·Hub 경로·의존성 규칙(`ontology → {spoke}`)·frontmatter 예제(`domain: ontology`)·spoke 표(실제 구현 5 + 계획 3 구분, `sample`/`adapters`는 BC 아님 명시)·grep 예제를 전부 교정. 근거 3개 SSOT 명시: master §11 · `ontology/_docs/star-craft-pipeline.md`(`type: hub, domain: ontology`) · `braindead/_docs/rule.md`. 이전 `star-craft-pipeline.md` 정합화(v-log 하단 참조)에서 누락됐던 child 스펙 갱신을 완결.

### Notes
- 백엔드 전반 규칙 감사에서 도출된 문서-코드 불일치를 우선 정리한 항목. 코드 레벨 위반(예: `mfds_user↔mfds_admin` Spoke↔Spoke 결합, `admin_auth_interactor`의 `HTTPException` 침투, `titanic`의 Schema=DTO 혼용, 일부 output port의 ORM 노출)은 별도 후속 과제로 남김 — 알려진 위반은 `_docs/CLAUDE.md` Harness Validation 체크리스트 하단에 명시.

## [v0.3.0] - 2026-07-21

### Removed
- **로컬(이메일/비밀번호) 회원가입·로그인 전면 폐지 — 소셜(OAuth) 가입만 허용.** `POST /auth/signup`·`POST /auth/login`·`POST /auth/refresh`·`DELETE /auth/logout`(모두 `auth_router.py`) 제거. 로컬 전용 파일 삭제: `auth_router.py`·`auth_schema.py`·`auth_mapper.py`·`auth_interactor.py`·`app/ports/input/auth_use_case.py`. `SignupCommand`·`LoginCommand` DTO 제거(`UserSessionDTO`는 OAuth·Redis 세션이 사용하므로 유지).
- **`PATCH /mypage/password` 제거** — 소셜 전용 계정은 비밀번호가 없어(`hashed_password=None`) 항상 실패하던 무의미 엔드포인트. `PasswordUpdateRequest` 스키마와 `security.hash_password`/`verify_password` import도 정리.

### Changed
- **`DELETE /mypage/withdraw`를 토큰 전용으로 변경** — 기존에는 비밀번호 입력을 요구해 소셜 유저가 탈퇴 불가능했음. 이제 인증 토큰만으로 탈퇴 처리.
- **역할 하드코딩(`role=EXPERT`) 불일치 제거.** `auth_pg_repository`를 `find_all_active` 한 메서드로 축소하고(리포트 스케줄러 배치용) 하드코딩 `EXPERT`를 기본값 `GENERAL`로 교체 — 역할의 SSOT는 화이트리스트(관리자 승격)이며 토큰 발급 시점에 결정된다는 규칙(v0.2.8)과 일관화. `AuthRepository` 포트도 `find_all_active`만 남기고 로컬 인증·세션·화이트리스트 조회 메서드 전부 제거. `dependencies/auth.py`는 `get_auth_repository`만 유지(`get_auth_use_case` 삭제).

### Notes
- 세션 저장소 이원화(로컬=PG / OAuth=Redis) 불일치는 로컬 인증 제거로 자연 해소 — 이제 세션은 OAuth의 Redis 스토어 단일 경로.
- 검증: 컨테이너 내 라우터 import 스모크 테스트 통과 — `/auth/signup·login·refresh·logout`·`/mypage/password` 부재 확인, `/auth/{provider}/login·callback`·`/mypage/withdraw` 잔존. `report_scheduler`·`daily_report` 배선 import 정상.
- **프론트엔드 후속 필요(별도 범위)**: `app/signup`(`auth/signup`)·`app/login`(`/api/auth/login`)·`app/mypage/password`(`/api/mypage/password`) 페이지가 제거된 엔드포인트를 호출 → 소셜 로그인 진입점으로 정리 필요. 기존 이메일 가입 계정은 로그인 경로가 사라져 접근 불가.

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
