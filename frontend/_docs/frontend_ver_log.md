# Frontend Version Log

## [v0.1.15] - 2026-07-20

### Removed
- **구 화이트리스트 관리 페이지 정리** — 회원 관리(`/admin/members`)로 기능이 대체되어 중복된 `app/admin/whitelist/page.tsx` 삭제. 관련 참조도 전부 제거: 사이드바 nav 항목(`lib/admin/admin-nav.ts`, 미사용 `UserCheck` import 포함), 헤더 타이틀 매핑(`components/admin/admin-header.tsx`), 대시보드 퀵링크(`app/admin/page.tsx`)를 각각 **회원 관리(`/admin/members`)**로 교체·정리.

### Notes
- 검증: 재컴파일 후 `/admin/members` **200**, `/admin/whitelist` **404**.

## [v0.1.14] - 2026-07-20

### Added
- **어드민 회원 관리 페이지** `app/admin/members/page.tsx` — 가입 회원 목록(이메일·이름·가입경로·상태[전문가/일반]·가입일·마지막로그인)을 표로 보여주고, 행별 **전문가 승격 / 승격 해제** 토글(`POST /admin/members/{email}/promote|demote`). 사이드바에 "회원 관리" 항목 추가(`lib/admin/admin-nav.ts`, `Users` 아이콘, 화이트리스트 위).

### Changed
- 회원가입 후 리다이렉트를 역할에 따라 분기 — 전문가로 승격된 계정만 `/mypage/industry`(업종 온보딩), 신규 일반회원은 `/mypage`로(`app/signup/page.tsx`). 화이트리스트 개편으로 신규 가입자는 일반회원이므로 전문가 전용 페이지에서 튕기는 문제 방지.
- 이용약관 제3조를 새 가입 흐름에 맞게 개정 — "화이트리스트 이메일만 전문가 가입" → "누구나 일반회원 가입, 운영자 승인으로 전문가 승격"(`app/terms/page.tsx`).

## [v0.1.13] - 2026-07-20

### Added
- **소셜 로그인 실제 OAuth 연동** — 카카오·네이버·Google 버튼을 목(mock)에서 **백엔드 OAuth 시작 URL로 top-level 이동**으로 교체(`app/login/page.tsx`·`app/signup/page.tsx`). `lib/oauth-url.ts`의 `socialLoginUrl(provider)`가 `${NEXT_PUBLIC_API_URL}/auth/{provider}/login` 생성(Next 프록시 우회 — 302 체인 정상화).
- **OAuth 콜백 페이지** `app/auth/callback/page.tsx` — 백엔드가 fragment(`#access_token=…&refresh_token=…`)로 넘긴 토큰을 localStorage에 저장(주소창에서 즉시 제거), `auth-state-change` 전파 후 `/mypage`로 이동. 토큰 없으면 `/login?oauth_error=1`로.
- login 페이지에 `oauth_error` 쿼리 감지 → 실패 안내 문구 표시.

### Removed
- 기존 소셜 버튼의 목(mock) 핸들러(`startMockSocialSignIn` 가짜 JWT 발급, signup no-op) 제거 — 실제 백엔드 OAuth로 대체.

## [v0.1.12] - 2026-07-20

### Added
- **소셜 로그인 카카오·네이버 버튼** 추가 (`app/login/page.tsx`·`app/signup/page.tsx`) — 스크린샷 레퍼런스대로 카카오(노랑 `#FEE500`·검정 말풍선 아이콘)·네이버(초록 `#03C75A`·흰 N 아이콘)·Google 순서로 배치. 세 버튼을 `<div className="space-y-3">`로 묶고 기존 Google 버튼 스타일(`h-12 w-full`·outline·hover shadow)을 그대로 미러링.
- 공유 아이콘 컴포넌트 `components/icons/social-icons.tsx`(`KakaoIcon`·`NaverIcon`, `currentColor` 단색 SVG) 신규 — 두 페이지에서 재사용.

### Changed
- login 페이지의 "Google 전용" 문구를 소셜 일반 문구로 정정(좌측 패널 부제·OAuth 배지·카드 설명).
- 로그인 소셜 목(mock) 핸들러를 `startMockSocialSignIn(setLoading, profile)` 헬퍼로 통합(Google·카카오·네이버 공용). provider별 가짜 JWT 발급 후 `/mypage` 이동. **실제 OAuth는 미연동**(백엔드 소셜 엔드포인트 부재) — 기존 Google 목과 동일한 데모 동작.

### Fixed
- 기존 Google 목 핸들러가 한글 이름(`구글 사용자`)을 `btoa`에 직접 넣어 비 Latin1 문자에서 예외가 나던 잠재 버그를, 헬퍼의 UTF-8 안전 base64 인코딩(`TextEncoder`)으로 해소 — 세 소셜 버튼 모두 정상 동작.

## [v0.1.11] - 2026-07-16

### Added
- Admin 사이드바 "크롤러/스크래퍼" **아래**에 **"수집 결과"** 메뉴(`/admin/scout/results`, `Database` 아이콘) 추가 (`lib/admin/admin-nav.ts`, 같은 "데이터 수집" 섹션). 페이지(`app/admin/scout/results/page.tsx`)는 탭 콘솔(`components/admin/scout/scout-results.tsx`) — `Tabs`로 크롤러/스크래퍼 전환, resources에 저장된 결과(`GET /api/scout/results`, backend_ver_log v0.2.3)를 테이블로 표시(크롤러: 저장시각·URL·제목·매칭키워드 / 스크래퍼: +길이·스니펫). 최신순, 새로고침 버튼, URL 새 탭 링크, `saved_at` unix초→로컬시간 포맷. 인증은 `adminFetch`.
- BFF 프록시 `app/api/admin/scout/results/route.ts` 신규 — 캐치올보다 우선하는 전용 GET 라우트로 `/api/scout/results`에 프록시(`proxyToBackend`가 `?kind=&limit=` 쿼리 자동 전달).

## [v0.1.10] - 2026-07-16

### Fixed
- **Vercel 빌드 실패(`ENOENT ... .next/routes-manifest-deterministic.json`) 해결** — Root Directory=`frontend`인 Vercel은 모노레포 루트 기준으로 파일 트레이싱을 하는데, "Both outputFileTracingRoot and turbopack.root are set" 경고를 없애려 `next.config.mjs`에 `outputFileTracingRoot: projectRoot`(=frontend)를 강제한 것이 원인이었음 — Vercel의 `onBuildComplete`가 `.next` 매니페스트를 레포 루트에서 찾다가 못 찾아 실패. Turbopack/webpack 무관하게 재현됨(빌드 도구 문제가 아니라 트레이싱 루트 문제). 해결: 해당 라인 제거 + 빌드 스크립트를 `next build`로 원복(직전 성공 커밋 `admin개선`과 동일 설정). 그 경고는 무해하며 성공 빌드에도 있었음. → 커밋 `0c62155`에서 Vercel 프로덕션 빌드 통과 확인.

### Added
- Admin 사이드바에 **"데이터 수집"** 섹션과 **"크롤러/스크래퍼"** 메뉴(`/admin/scout`, `Radar` 아이콘) 추가 (`lib/admin/admin-nav.ts`, 비전처리 섹션 아래). 페이지(`app/admin/scout/page.tsx`)는 탭 토글 콘솔(`components/admin/scout/scout-console.tsx`) — `Tabs`로 크롤러↔스크래퍼 전환, **사이트 주소(URL)·자연어 명령** 2개 입력창을 두고 실행하면 백엔드 스카우트(`POST /api/scout/run`, backend_ver_log v0.2.1)가 명령을 해석해 크롤/스크랩을 수행. 결과 패널에 AI 해석 문장·해석된 파라미터(페이지·깊이·키워드)·실행 요약(방문/적재/스크랩 수) 표시. 인증은 `adminFetch`로 admin JWT 전달.
- BFF 프록시 `app/api/admin/scout/route.ts` 신규 — 캐치올(`app/api/admin/[...path]`)이 `/admin/*`만 백엔드 `/admin/*`로 보내므로, `/api/scout/run`으로 보내는 전용 라우트를 별도로 둠(`proxyToBackend`, 크롤 지연 대비 timeout 120s, `Authorization` 전달).
- 결과 요약 라벨에 `findings_saved`("저장된 관련 URL") 추가 — 크롤러가 resources에 저장한 관련 URL 수 표시(backend_ver_log v0.2.2).

### Removed
- **Admin auth 바이패스(`ADMIN_AUTH_BYPASSED` / `NEXT_PUBLIC_ADMIN_SKIP_AUTH`) 완전 제거.** "FastAPI 배포 전 임시" 셔틀이었으나 기본값이 `!== "false"`라 **환경변수 미설정 시 자동으로 로그인 우회**되는 구조였음 — Vercel처럼 `.env.local`이 안 실리는 환경에서 비밀번호 없이 대시보드 진입·로그아웃 무효·일부 API 401(무토큰 호출) 증상의 근본 원인. `lib/admin/auth.ts`, `app/admin/layout.tsx`, `app/admin/login/page.tsx`에서 관련 분기 전부 삭제 → 어드민은 항상 로그인 필수.

### Changed
- Admin 진입 게이트가 토큰 **존재 여부만** 확인해, 만료·형식오류(stale) 토큰을 들고 있으면 `/admin/dashboard`가 401만 반복하고 로그인 화면으로 못 튕기던 문제 개선. `lib/admin/auth.ts`에 `isAdminTokenValid()` 추가(형식·`role==="admin"`·`exp` 만료 검사, 요청 중 만료 회피용 10초 여유) 후 `isAdminLoggedIn()`이 이를 사용. `decodeAdminJwtPayload` 반환 타입에 `exp` 포함. `app/admin/layout.tsx` 진입 시 토큰이 무효면 `removeAdminSession()`으로 stale 세션 정리 후 `/admin/login`으로 이동. 서명 검증은 여전히 백엔드(`admin_auth_middleware.verify_admin_token`) 소관.

## [v0.1.8] - 2026-07-15

### Changed
- 법규채팅(`app/api/regulation-chat/route.ts`)과 원료분석채팅(`app/api/analysis-chat/route.ts`)을 백엔드 **시맨틱 게이트웨이**(`/api/gateway/ask`, backend_ver_log v0.2.0) 프록시로 전환. 기존의 백엔드 `/regulation-chat`·`/analysis-chat` 직접 호출과 프론트 측 Gemini/법령 RAG fallback(`@/lib/server/gemini-generate`, `@/lib/server/law-api`)을 제거 — 질문 유형 분기·감사로그·rate limit이 게이트웨이에서 일괄 적용됨. UI 계약은 유지(`{ reply, session_key, ... }`)하되 `destination` 필드 추가. E2E: 법규채팅 `dest=rag`, 원료분석채팅 `dest=general`로 게이트웨이 경유 및 `gateway_audit_logs` 적재 확인.
- 위 전환으로 `regulation-chat`의 `referenced_laws`는 빈 배열, `company_type`(업종 필터)은 미사용이 됨(게이트웨이 rag 응답이 아직 참조 법령·업종을 반환하지 않음). 랜딩 도우미(`app/api/gemini/chat/route.ts`)는 삭제 예정이라 미변경.

## [v0.1.7] - 2026-07-03

### Added
- Admin 사이드바에 "비전처리" 섹션과 "이미지 업로드" 메뉴(`/admin/vision/images`) 추가 (`lib/admin/admin-nav.ts`). 업로드 폼(`components/admin/vision/image-upload-form.tsx`)에서 png/jpg/jpeg/gif/webp/bmp 이미지를 선택·미리보기·업로드할 수 있음.
- `app/api/admin/vision/images/route.ts` 신규 BFF 프록시 추가 — 기존 범용 캐치올(`app/api/admin/[...path]/route.ts`)은 `request.text()`로 바디를 다뤄 바이너리(이미지) 업로드 시 데이터가 손상되므로, `request.formData()`로 파싱해 새 `FormData`로 재전송하는 바이너리-세이프 전용 라우트를 별도로 둠 (`app/api/lesson/titanic/james/upload/route.ts`와 동일 패턴 + `Authorization` 헤더 전달). 백엔드 `POST /api/vision/images`(backend_ver_log v0.1.11)로 프록시.

## [v0.1.6] - 2026-07-03

### Changed
- `app/signup/page.tsx`: 가입 성공 시 백엔드가 반환하는 `access_token`(backend_ver_log v0.1.9)을 `localStorage`에 저장하고 `/mypage/industry`로 즉시 이동하도록 변경. 기존에는 성공 메시지만 보여주고 끝나 사용자가 `/login`에서 다시 로그인해야 사이드바의 "업종/관심 설정" 버튼(`components/mypage/sidebar.tsx`)이 동작했음 — 이제 가입 직후 바로 접근 가능. 더 이상 쓰이지 않는 `successMessage` 상태·UI 제거.

## [v0.1.5] - 2026-07-02

### Fixed
- "식중독 통계" 페이지가 열릴 때마다 동일 외부 API를 최대 6회(연도별/원인물질별/시설별 × 캐시시도+refresh 재호출) 호출하던 문제. `app/api/food-stats/{yearly,by-agent,by-facility}/route.ts`를 백엔드 `GET /food-stats/*`(DB 기반, backend_ver_log v0.1.5) 프록시로 교체하고, `lib/server/food-stats-*.ts`의 라이브 fetch 코드는 제거해 정적 fallback 배열만 최종 안전망으로 남김.
- `app/recalls/stats/page.tsx`의 중복 `refresh:true` 재호출 블록, `lib/phase3-client.ts`의 관련 `refresh` 파라미터 제거.

## [v0.1.4] - 2026-07-02

### Fixed
- "위해요소 리콜" 목록이 최초 진입 시 오래된 mock/캐시 데이터를 잠깐 보여주다 실제 데이터로 바뀌던 현상 — `app/api/recalls/**` BFF가 "캐시 우선 렌더 + 즉시 refresh 재호출(라이브 외부 API)" 이중 구조였던 것을 제거하고, 항상 백엔드 DB(`/recalls`, `/recalls/latest`, `/recalls/food-types`, `/recalls/{id}`)만 프록시하도록 정리. 웜 응답 최대 8~9초 → 수십ms.
- `lib/server/read-mfds-cache.ts`가 존재하지 않는 경로(`backend/apps/data`)를 찾던 버그 수정 — 실제 캐시 위치(`backend/apps/mfds_user/data`)로 정정 (Docker 배포에선 어차피 해당 디렉터리가 마운트 안 되어 효과 없고, 로컬 비-Docker 개발 환경에서만 유효).

### Removed
- `lib/server/food-safety-recall.ts`(라이브 외부 API 호출 전용, 더 이상 참조되지 않음) 삭제. `lib/server/recalls-catalog.ts`에서 라이브 호출 관련 함수 제거.

## [v0.1.3] - 2026-07-02

### Changed
- 랜딩 네비게이션의 "수업용" 링크를 관리자 사이드바로 이동(`lib/admin/admin-nav.ts`), `/lesson/**` 라우트를 `/admin/lesson/**`로 이동 — admin 로그인 뒤에서만 접근 가능하도록. `components/lesson/lesson-sidebar.tsx`를 랜딩 상단바 기준 고정 포지셔닝에서 admin 본문 영역에 나란히 배치되는 구조로 재작성.

## [v0.1.2] - 2026-07-01

### Fixed
- `/admin/data-sync` 페이지가 호출하던 백엔드 API가 없어(404) 항상 에러만 뜨던 문제 — 백엔드에 실제 엔드포인트 추가하고 연동.
- 동기화 트리거 성공 메시지가 존재하지 않는 `data.count` 필드를 참조하던 버그 — 백엔드 `message` 필드를 그대로 표시하도록 수정.

### Added
- 페이지 상단에 "마지막 동기화" 요약 카드 추가 (`last_sync_at`/`sync_wave`/`sync_slot` 표시).

## [v0.1.1] - 2026-07-01

### Changed
- `/lesson/braindead/*`(메일·주소록·텔레그램·디스코드·수신함) 전체를 `/admin/braindead/*`로 이동 — 보안을 위해 admin 로그인 뒤에 배치. 컴포넌트를 `components/lesson/lesson-*` → `components/admin/braindead/*`로 이동·이름 변경(`Braindead*`), `adminFetch`로 통일해 토큰을 자동 첨부.
- 개별 BFF route.ts(`app/api/lesson/braindead/*`) 4개를 삭제하고, 기존 `app/api/admin/[...path]/route.ts` catch-all 프록시에 `braindead` 분기(→ 백엔드 `/api/braindead/*`)를 추가해 재사용.
- `NEXT_PUBLIC_ADMIN_SKIP_AUTH=false`로 설정해 admin 로그인 게이트를 실제로 활성화(기존엔 기본 우회 상태였음).
- Admin 사이드바(`admin-nav.ts`, `admin-sidebar.tsx`)에 "자동화" 섹션 헤더 + 5개 메뉴 추가. `lesson-sidebar.tsx`에서 자동화 섹션 제거.
- `lib/admin/auth.ts`의 `adminFetch`가 `FormData` 바디일 때 `Content-Type`을 강제하지 않도록 수정(CSV 업로드 지원).

### Fixed
- `next.config.mjs`의 `/api/admin/:path*` rewrite가 `app/api/admin/[...path]/route.ts`(동적 라우트)보다 먼저 적용되어 route.ts가 전혀 실행되지 않던 문제 발견·제거 — Next.js는 배열 형태 rewrites를 동적 라우트보다 먼저 적용함.

### Removed
- `lib/api-path.ts`의 `contactsUploadUrl`/`contactsSearchUrl`/`contactsListUrl`/`inboxListUrl` (더 이상 사용되지 않음, `adminFetch`로 대체).

## [v0.1.0] - 2026-07-01

### Added
- `/lesson/braindead/inbox` 페이지 — n8n이 `POST /braindead/inbox/receive`로 전달한 수신 메일 목록을 표시. 항목 클릭 시 본문 전체를 다이얼로그로 확인 가능.
- `lesson-sidebar.tsx`에 "5. 수신함" 메뉴 추가.
- `lib/api-path.ts`에 `inboxListUrl()` 추가.
