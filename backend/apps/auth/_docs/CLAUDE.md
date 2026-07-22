---
type: spoke
domain: auth
links:
  - ontology
---

# `apps/auth` — 인증 게이트웨이 (Auth BC) 실행 스펙

> **이 파일이 SSOT입니다.** 같은 폴더의 [`auth-gateway-harness.md`](auth-gateway-harness.md)는 강사가 제공한 **원본 지시서(일반 템플릿)** 로, 우리 아키텍처(fractal 11-file · hexagonal · star topology)와 어긋나는 부분을 이 문서가 재해석·확정했다. 두 문서가 충돌하면 **이 문서가 우선**한다.
>
> 상위 스펙: [`../../../CLAUDE.md`](../../../CLAUDE.md)(master) > [`../../_docs/CLAUDE.md`](../../_docs/CLAUDE.md)(backend) > this file.

---

## 0. 역할 · 목표

- **발급은 auth에서만, 검증은 어디서나(공개키).** JWT 발급(개인키)은 이 BC 안에만 존재하고, 검증은 `core/matrix` 공유커널이 공개키만으로 수행한다.
- 최종 목표는 인증 전용 컨테이너(auth 서브도메인) 분리 배포이나, **먼저 모놀리스 안에서 BC로 완성·검증 후** 분리한다(§6 Phase 6).

## 1. 확정 결정 (2026-07-22, 사용자 승인)

| # | 결정 | 내용 |
|---|---|---|
| D1 | **병렬 신설** | 기존 HS256 인증(`mfds_user`·`mfds_admin`)은 **한 줄도 수정하지 않고** 그대로 두고, `apps/auth`를 새로 만든다. 기존 앱의 이관은 별도 후속 작업. |
| D2 | **RS256 비대칭** | 개인키(`JWT_PRIVATE_KEY`)는 발급부에만, 검증은 공개키(`JWT_PUBLIC_KEY`)로. |
| D3 | **코드 먼저, 분리 배포는 이후** | 모놀리스 내 BC로 완성·검증(Phase 0~5) 후, `auth_main.py`·docker 서비스·cloudflared 분리는 Phase 6. |

## 2. 절대 규칙 (원본 §1 재해석 — 위반 시 작업 중단 후 보고)

1. 기존 앱(`mfds_user`, `mfds_admin`, `ontology`, `braindead`, `titanic`, `siliconvalley`) 코드는 수정하지 않는다. 예외는 Phase 5의 RoleChecker 예시 1개 앱 — 그때 명시 승인을 받는다.
2. `docker-compose.server.yml`의 신규 auth 서비스에 `ports:` 매핑을 추가하지 않는다(진입은 cloudflared만).
3. JWT 검증부의 허용 알고리즘은 `algorithms=["RS256"]` **리터럴 하드코딩**. 환경변수·설정으로 빼지 않는다.
4. `JWT_PRIVATE_KEY`를 읽는 코드는 **발급 어댑터(`adapter/outbound/token/`)에만** 존재한다. 검증 경로에서 개인키 참조 발견 시 즉시 수정.
5. 발급 어댑터는 **호출 시점**에 개인키를 읽는다 — 백엔드 컨테이너에서 모듈 import만으로 키 부재 에러가 나면 안 된다.
6. 비밀키·개인키·PEM·`.env.*`를 저장소에 커밋하지 않는다(`.gitignore` 등재).
7. **다른 앱이 `apps.auth`를 import하는 코드를 작성하지 않는다.** 다른 앱이 쓸 수 있는 것은 `core/matrix` 검증 커널뿐. (star topology의 spoke→spoke 금지와 동일 원리 — importlinter로 강제, Phase 6.)

## 3. 구조 — 원본 flat 4파일의 fractal 전개

원본 `router.py / services.py / schemas.py / rbac.py`를 우리 헥사고날로 매핑:

```
apps/auth/
├── adapter/inbound/api/v1/auth_router.py           # ← router.py
├── adapter/inbound/api/schemas/auth_schema.py      # ← schemas.py
├── adapter/inbound/mappers/auth_mapper.py          # schema ↔ dto 경계 톨게이트
├── app/ports/input/auth_use_case.py                # IAuthUseCase (Driving Port)
├── app/use_cases/auth_interactor.py                # ← services.py 오케스트레이션
├── app/ports/output/token_issuer_port.py           # ITokenIssuerPort
├── app/ports/output/refresh_session_port.py        # IRefreshSessionPort
├── app/ports/output/oauth_provider_port.py         # IOAuthProviderPort
├── app/ports/output/identity_port.py               # IIdentityPort (§7-I2 결정 후)
├── app/dtos/auth_dto.py                            # TokenBundle, LoginCommand, Identity …
├── adapter/outbound/token/rs256_token_issuer.py    # 개인키 발급 (규칙 4·5)
├── adapter/outbound/session/redis_refresh_session.py  # grid_redis_manager 재사용
├── adapter/outbound/oauth/google_provider.py       # grid_google_oauth_manager 재사용
├── adapter/outbound/oauth/kakao_provider.py        # 범위 확인 후 (§7-I5)
├── domain/value_objects/role.py                    # ← rbac.py — Role/Permission 매핑은 도메인 정책
├── domain/entities/refresh_session_entity.py
├── dependencies/auth_provider.py                   # Composition Root (DIP)
└── _docs/CLAUDE.md                                 # this file
```

- DB 테이블이 없는 엔드포인트 중심 BC라 orm/orm_mapper/repository는 refresh 세션이 Redis 전용인 한 생략(§12 프랙탈 세트의 합리적 축소). identity를 자체 저장(§7-I2-a)하게 되면 그때 11-file 풀세트로 확장.
- **라우터 최초 검증**: 비즈니스 엔드포인트보다 먼저 `GET /auth/myself`로 전체 배선(라우터→인터랙터→포트) 왕복을 확인한다(master §12).

### 엔드포인트 (원본 §2.1 → prefix만 조정)

| Method | Path | 설명 |
|---|---|---|
| GET | `/auth/myself` | 배선 검증 (최우선 구현) |
| POST | `/auth/login` | 로그인 → 토큰 발급 |
| POST | `/auth/logout` | jti 블랙리스트 + refresh 폐기 |
| POST | `/auth/refresh` | 로테이션 재발급 |
| GET | `/auth/callback/{provider}` | OAuth 콜백 |
| GET | `/.well-known/jwks.json` | 공개키 JWK(kid 포함) — 외부 검증자용 |

> prefix `/auth`: 초기엔 옛 `mfds_user`의 `/auth/*` 충돌을 피해 `/authz`를 썼으나, auth를 별도 도메인(`auth.foodopenlab.com`)으로 분리 + 옛 소셜 로그인 폐기(2026-07-22)로 충돌이 사라져 **`/auth`로 전환**했다. (Redis 내부 키의 `authz:` 네임스페이스는 URL과 무관하게 유지)

## 4. core 공유커널 — 검증부 (원본 §2.2 검증부 + §2.3)

원본의 `core/security.py`·`core/dependencies.py` 대신 우리 스타일의 매트릭스 매니저 **1개 신설**:

```
core/matrix/grid_seraph_token_guard_manager.py   # Seraph = 매트릭스의 문지기
├── verify_token(token: str, aud: str) -> TokenPayload
│     # jwt.decode(token, JWT_PUBLIC_KEY, algorithms=["RS256"], audience=aud)
├── get_current_user(request) -> TokenPayload
│     # 쿠키 또는 Authorization 헤더에서 추출 → verify_token
│     # + Redis jti 블랙리스트 조회(즉시 차단 계정)
└── RoleChecker(*allowed: Role)                   # roles 클레임 검사, 미충족 403
```

- 기존 `grid_admin_guard_manager.py`(HS256 어드민 검증)와 **병렬 공존**(D1). 건드리지 않는다.
- `core/` → `apps/` import 금지(master §11)이므로 `Role` enum이 필요하면 커널에 미러 정의하거나 str 비교로 처리 — **커널이 `apps.auth`를 import하지 않는다.**

## 5. 토큰 스펙 (원본 §2.2)

- **Access token 클레임**: `sub`, `roles`(list), `aud`, `exp`, `iat`, `jti` + 헤더 `kid`. 만료 기본 10분.
- **aud**: 모놀리스 단계는 단일 `foodopenlab-api`. 분리 배포 시 서비스별 상이(교차 사용 불가). 원본의 `ragtailor-*`는 강사 환경 플레이스홀더.
- **쿠키**: `secure=True, httponly=True, samesite="lax"` + Phase 6부터 `domain=".foodopenlab.com"` (auth 서브도메인 발급 쿠키를 api·www가 공유). 그 전 로컬 검증은 domain 미지정.
- **Refresh token**: opaque 랜덤(`secrets.token_urlsafe`) → **SHA-256 해시만 Redis 저장**, **로테이션** 방식. **재사용 감지 시 해당 사용자 세션 전체 폐기.** Redis 키(Phase 3 구현 확정):
  - `authz:refresh:{token_hash}` → hash{status, sub} (TTL=refresh 수명, 기본 14일 / `AUTH_REFRESH_TTL_SEC`)
  - `authz:user:{sub}:tokens` → set(token_hash…) (sub 전체 폐기용)
  - `authz:jti:block:{jti}` → "1" (즉시차단, TTL=access 잔여수명)
  - 로그아웃 시 access jti를 블랙리스트에 등록. **jti 블랙리스트 조회를 `get_current_user`에 주입하는 배선은 Phase 4**(라우터/인터랙터 조립 시).
- **키 생성**: `scripts/generate_jwt_keys.sh` (openssl RSA 2048, PEM → env 주입은 base64 인코딩 방식). PEM은 `.gitignore`.

## 6. Phase 로드맵 (커밋 단위)

> **진행 현황 (2026-07-22):** Phase 0~6 **완료 + 배포 라이브**. 이후 **인증 전면 통합(A안) 진행 중** — 유저·어드민 로그인을 auth(RS256)로 일원화. A1(admin 화이트리스트+토큰 email/name/roles)·A2(백엔드 검증 RS256 전면교체) 완료. URL prefix `/authz`→`/auth` 전환, `keys/`·중복 redirect 정리, 옛 소셜 로그인(mfds_user oauth) 언마운트. auth 테스트 28 통과. **남은 것: A3 프론트 컷오버(+auth 콜백 리다이렉트), A5 admin google/docs 컷오버·옛 코드 삭제.**
> - hot-path 최적화: `get_current_user`의 jti 조회는 `asyncio.timeout(0.2)`로 감싸 Redis 장애 시 **빠른 fail-open**(느린 fail-open 방지). 인증 검증이 모든 요청을 타는 경로라 적용.

### 6.2 배포 산출물 & 운영 단계 (Phase 6)

**두 compose 파일 구분 (중요):**
- **`docker-compose.yaml`** = 현재 이 서버에서 실행 중인 파일. `build: ./backend` + `volumes: ./backend:/app`(코드 실시간 마운트). **auth 서비스는 여기 추가함.** Hub 불필요 — 서버에서 직접 빌드.
- `docker-compose.server.yml` = 다른 원격 서버용(Hub 이미지 pull, 코드 구워넣음). 현재 미사용. 그쪽으로 배포할 땐 auth를 Hub 변형으로 별도 추가 필요.

**추가된 코드/설정:**
- `backend/auth_main.py` — 인증 전용 엔트리포인트(`uvicorn auth_main:app --port 9000`, CORS `allow_credentials=True`, docs 비노출).
- `docker-compose.yaml` `auth` 서비스 — `build: ./backend` + 코드 마운트, `command: uvicorn auth_main:app ... 9000`, **ports 무노출**, `container_name: auth`(cloudflared가 `http://auth:9000` 해석), `env_file: [.env, .env.auth]`. cloudflared `depends_on`에 `auth`.
- `backend/.env.auth.example` · `backend/.importlinter`(`auth-isolation` + `auth-selfcontained`).

**⚠️ 운영 단계 (서버에서 직접, Hub 불필요):**
1. **키 생성**: `cd ~/projects/com.foodopenlab && bash backend/scripts/generate_jwt_keys.sh` → 출력 base64를 신규 `backend/.env.auth`에 채움.
2. **backend 검증키**: `backend/.env`에 `JWT_PUBLIC_KEY_B64=<공개키>` + `SERVICE_AUD=foodopenlab-api` 추가(개인키 금지).
3. **기동**: `docker compose up -d --build auth` (코드는 bind-mount라 backend는 `docker compose restart backend`로 새 `/auth`·검증 반영).
4. **확인**: `https://auth.foodopenlab.com/healthz` → `{"ok": true}`.
5. **importlinter(선택)**: `pip install import-linter && (cd backend && PYTHONPATH=apps:core lint-imports)`.

> 왜 Hub가 필요 없나: 개발자=서버가 같은 머신이고 코드가 컨테이너에 bind-mount되므로, 코드를 다른 머신으로 나를 필요가 없다. Hub는 '두 머신 사이 코드 운반' 용도라 이 구성엔 불필요.

| Phase | 내용 | 원본 대응 | Acceptance Criteria |
|---|---|---|---|
| **0** | 키 스크립트 + `.gitignore` + 스켈레톤 + `/auth/myself` | §2.7, §2.1 | main.py 기동 시 import 에러 0 · `/auth/myself` 200 |
| **1** | `grid_seraph_token_guard_manager` + 단위테스트 | §2.2 검증부, §2.3 | 만료·서명변조·`alg=none`·`alg=HS256` 강제·aud 불일치 **전부 거부** 테스트 |
| **2** | RS256 발급 어댑터(클레임 §5, 호출 시점 키 로드) | §2.2 발급부 | 발급→공개키 검증 왕복 통과 · `JWT_PRIVATE_KEY` 없이 main.py import 정상 |
| **3** | Redis refresh 로테이션 + 재사용 감지 + jti 블랙리스트 | §2.1 | 재사용 → 세션 전체 폐기 테스트 |
| **4** | login/logout/refresh/callback 인터랙터·라우터 + jwks.json | §2.1 | 엔드포인트 통합 테스트 · **착수 전 §7-I2 결정** |
| **5** | `role.py` RBAC + 예시 1개 앱에 `RoleChecker` 적용 | §2.5 | 대상 앱은 사용자에게 질문 후 |
| **6** | `auth_main.py` + docker `auth` 서비스(ports 없음) + `.env.auth`/`.env.backend` 분리 + cloudflared `auth.foodopenlab.com` 라우팅(§6.1) + `.importlinter`(실제 앱 목록) | §2.4·2.6·2.8·2.9 | auth 단독 기동 `/healthz` 200 · `https://auth.foodopenlab.com/healthz` 200 · lint-imports 통과 |

### 6.1 cloudflared 라우팅 (원본 §2.8의 우리 실정 재해석)

원본은 로컬 `config.yml` ingress 편집을 지시하나, **우리 cloudflared는 토큰 모드**(`docker-compose.server.yml`: `tunnel run --token ${CLOUDFLARE_TUNNEL_TOKEN}`)라 ingress가 **Cloudflare Zero Trust 대시보드에서 원격 관리**된다. 따라서 Phase 6의 터널 작업은 코드가 아니라 대시보드 수동 적용이다:

1. Zero Trust → Networks → Tunnels → (해당 터널) → **Public Hostname 추가**:
   - `auth.foodopenlab.com` → Service `http://auth:9000` (docker 네트워크 내부명)
   - 기존 `api.foodopenlab.com` → `http://backend:8000` 유지
2. DNS 라우트는 Public Hostname 추가 시 자동 생성(CNAME). CLI 사용 시: `cloudflared tunnel route dns <터널> auth.foodopenlab.com`
3. `auth` 서비스는 `cloudflared`와 같은 docker 네트워크에 두고 `ports:` 미노출(§2 규칙 2). `cloudflared`의 `depends_on`에 `auth` 추가.

> 참고: 기존 `backend` 서비스의 `ports: "18000:8000"`은 기존 구성(D1 — 손대지 않음). 신규 `auth`에만 무노출 원칙 적용.

- 각 Phase 완료 시 `backend/_docs/backend_ver_log.md` 기록(master Part VI).
- 원본 §2.9의 영화 앱 목록(harry_porter 등)은 강사 플레이스홀더 — 실제 소스 모듈: `mfds_user, mfds_admin, ontology, braindead, titanic, siliconvalley` (+`sample`, `adapters`).
- 원본 §2.4의 `login_gate.py`는 이 저장소에 **존재하지 않음** — 해당 지시 무시.

## 7. 오픈 이슈

| # | 이슈 | 상태 |
|---|---|---|
| I1 | **`/auth` prefix 충돌** — `mfds_user/oauth_router`가 `/auth/{provider}/login|callback` 점유 | 해소: 모놀리스 단계 `/auth` 사용(§3). Phase 6에서 `/auth` 전환 |
| I2 | **Identity 소유권** | 해소(2026-07-22): **(a) auth 자체 보유.** apps/auth가 자체 identity 테이블(`auth_identities`)을 갖고 OAuth 로그인 시 upsert. `sub`=auth 자체 id. mfds_user와 독립 → 분리 배포 자기완결성 확보. 통합은 I3로 보류. |
| I3 | **기존 HS256 이관** — D1로 당분간 공존. RS256 안정화 후 `mfds_user`/`mfds_admin`을 seraph 검증으로 갈아타는 별도 프로젝트 | 보류 |
| I4 | **기존 취약점(이관 시 정리)** — `mfds_user/app/services/token_service.py`의 하드코딩 폴백 시크릿(`"haccp_user_default_…"`), refresh 로테이션·재사용 감지 부재 | 기록만 (D1: 수정 금지) |
| I5 | **OAuth provider 범위** | 해소(2026-07-22): **Google + Kakao + Naver 3종.** env에 3종 CLIENT_ID/SECRET/REDIRECT_URI 존재. `mfds_user`의 어댑터를 **참조**(import 아님)해 apps/auth에 자기완결 provider 어댑터 복제(BC 간 정당한 중복). |
| I6 | **실제 도메인/aud 값** | 해소: `auth.foodopenlab.com` / `api.foodopenlab.com` 확정(2026-07-22, 사용자 확인). aud=`foodopenlab-api`, 쿠키 `domain=".foodopenlab.com"`(§5, §6.1) |

## 8. 원본 지시서 대응표 (auth-gateway-harness.md → this file)

| 원본 | 처리 |
|---|---|
| §0 컨텍스트 (ragtailor, 영화 앱) | 강사 환경 — foodopenlab 실정으로 치환(§5, §6) |
| §1 절대 규칙 | §2로 계승·강화 |
| §2.1 apps/auth flat 4파일 | §3 fractal 전개 |
| §2.2 core/security.py | 발급=apps/auth 어댑터, 검증=`grid_seraph_token_guard_manager`(§4) |
| §2.3 core/dependencies.py | §4 커널에 통합 |
| §2.4 auth_main.py / login_gate.py | Phase 6 / 파일 부재로 무시(§6) |
| §2.5 main.py 확인 | Phase 5 |
| §2.6 docker-compose | Phase 6 |
| §2.7 키 스크립트 | Phase 0 |
| §2.8 cloudflared | Phase 6, 수동 적용 지시로 출력 |
| §2.9 importlinter | Phase 6, 실제 앱 목록으로 |
| §3 완료 기준 | 각 Phase AC로 분배(§6) |
| §4 진행 방식 | 본 문서 전체가 그 이행 |
