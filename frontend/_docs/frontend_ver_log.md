# Frontend Version Log

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
