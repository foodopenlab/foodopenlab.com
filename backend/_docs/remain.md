# 남은 작업 (Remaining / Follow-ups)

> 최근 세션(회원가입 소셜 전환 · 백엔드 규칙 감사 정리 · 어드민 구글 로그인 · 보안 헤더)에서 파생된
> **미완료·후속 결정 항목** 모음. 완료된 것은 각 `_ver_log.md` 참고.
> 기준일: 2026-07-21

---

## 🔴 필수 — 운영에서 안 하면 기능이 막힘

### 1. ~~구글 콘솔에 어드민 콜백 redirect URI 추가~~ ✅ 완료 (2026-07-21)
- `https://api.foodopenlab.com/admin/auth/google/callback` 콘솔 등록 완료.
- (기존 유저용 `https://api.foodopenlab.com/auth/google/callback`은 그대로 유지)

### 2. 프론트 `NEXT_PUBLIC_API_URL` 확인
- `https://api.foodopenlab.com` 이어야 함 (어드민 구글 로그인 state 쿠키·콜백이 동일 도메인이어야 동작).
- 어드민 로그인 페이지(`app/admin/login`)는 재시작으로 반영됨. 배포 시 재확인.

### 3. 실제 구글 로그인 E2E 확인 — 🟢 대부분 완료 (2026-07-21)
- 자동 검증 통과(구글 동의 화면 제외 전 구간):
  - `/admin/auth/google/login`→302 구글+state 쿠키, 콜백 CSRF(state 불일치)→error, `/admin/members` 무인증→401, `/docs` 무쿠키→307 구글유도
  - 허용 `kcs8815@gmail.com`→admin JWT 발급·`admins` upsert / 비허용→거부(403)
  - 발급 JWT로 `/admin/members`(Bearer)→200, `/docs`·`/openapi.json`(세션쿠키)→200(실 Swagger UI)
  - 프론트 `/admin/login`→"Google 계정으로 로그인" 버튼 렌더, 구 비번폼 제거
- **남은 것(사람이 브라우저로 1회)**: 실제 구글 동의화면 클릭 → `/admin` 진입 최종 확인. (redirect URI는 콘솔 등록 완료라 정상 예상)

---

## 🟡 후속 — 급하지 않음, 다음 배포/여유 있을 때

### 4. 백엔드 재빌드 → `Server: uvicorn` 헤더 제거
- `backend/Dockerfile` CMD에 `--no-server-header` 이미 반영됨. **재빌드 시 자동 적용**:
  ```
  docker compose up -d --build backend
  ```
- 경미한 정보 노출이라 **지금 당장 불필요**. 다음에 백엔드 재빌드할 일과 묶어서.

### 5. 프론트 CSP: Report-Only → Enforce 승격
- 현재 `next.config.mjs`의 CSP는 `Content-Security-Policy-Report-Only`(차단 없이 경고만).
- 절차: ① 사이트 실사용하며 브라우저 콘솔의 CSP 위반 수집 → ② 걸리는 출처를 CSP에 추가 튜닝 → ③ 키명을 `Content-Security-Policy`로 변경해 **차단 활성화**.

### 6. 보안 헤더 실측
- `securityheaders.com` / Mozilla Observatory에 `foodopenlab.com` · `api.foodopenlab.com` 입력해 실제(Cloudflare 경유) 점수 확인.

---

## 🟢 정리(cleanup) 후보 — 선택, 기능 영향 없음

### 7. 비밀번호 어드민 인증 잔재 제거 여부 결정
- 어드민 로그인이 구글로 완전 교체돼 아래가 **미사용**:
  - `.env`의 `ADMIN_EMAIL` / `ADMIN_PASSWORD` (이제 로그인·docs에 안 쓰임, `seed_admin.py`에만 잔존)
  - `seed_admin.py` (구글 전환으로 시드 불필요 — import 회귀는 v0.4.0에서 수정 완료)
  - `admin_auth_router.py`(언마운트된 `POST /admin/login`), `AdminAuthInteractor.login`(비번 검증) — dead code
  - `create_admin_token`은 구글 인터랙터가 재사용하므로 **존치 필요**
- 완전 삭제할지, 폴백용으로 남길지 결정 후 정리.

### 8. `AdminORM.hashed_password` — 구글 어드민은 랜덤 사용불가 해시로 채움
- 비번 로그인 폐지로 실제 의미 없음. 스키마 정리(nullable 전환 등) 시 마이그레이션 필요 → 당장은 현행 유지.

### 9. siliconvalley 구조 네이밍(§12 관례 불일치)
- 인터랙터 디렉토리가 `app/use_case`(단수) — 스펙은 `app/use_cases`(복수). 리네임 시 provider/import 다수 변경.
- dto의 `*Query`는 introduce_myself가 인자를 받지 않게 바뀌며 **미사용**(향후 POST 엔드포인트용으로 존치 가능).

---

## ✅ 참고 — 이번 세션에서 완료된 것 (재작업 불필요)
- 회원가입 소셜(OAuth) 전용 전환, 로컬 이메일/비번 가입·로그인 폐지 (backend v0.3.0 / frontend v0.1.16)
- 백엔드 규칙 감사 전 항목 정리: 문서 SSOT(Hub=ontology), interactor 프레임워크/ORM 침투 0, output port ORM 노출 0, Schema=DTO 혼용 0, DDD 공백(mfds_admin·siliconvalley 엔티티), `mfds_user↔mfds_admin` 공유 ORM → `core/matrix/orm` 공유 커널 (v0.3.1~v0.3.9)
- 어드민·`/docs` 구글 RBAC 로그인 (backend v0.4.0 / frontend v0.1.17)
- 보안 응답 헤더(CSP·클릭재킹·nosniff·Referrer·Permissions·HSTS) (backend v0.4.1 / frontend v0.1.18)
