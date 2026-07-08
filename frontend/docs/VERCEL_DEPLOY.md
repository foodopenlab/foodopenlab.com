# foodopenlab.com (Vercel) 배포 설정

## 왜 메인 Gemini만 되고 나머지는 503 Tunnel 오류가 났나

- `BACKEND_URL=https://www.foodopenlab.com` → **프론트(Vercel)를 백엔드로 프록시** (잘못된 설정)
- `BACKEND_URL`이 **ngrok** 등 터널 URL → 터널이 꺼지면 **`503 Tunnel Unavailable`**

이제 아래 API는 **Vercel의 Next.js Route Handler**가 직접 처리합니다 (터널·로컬 uvicorn 불필요):

| 경로 | 기능 |
|------|------|
| `/api/gemini/chat` | 랜딩 Gemini 채팅 |
| `/api/analysis-chat` | AI 원료 분석 채팅 |
| `/api/regulation-chat` | 법규 채팅 |
| `/api/recalls` | 회수·판매중지 목록 (식품유형 5건 / 전체 최대 100건) |
| `/api/recalls/food-types` | 회수 DB 식품유형 목록 |
| `/api/recalls/latest` | 최신 회수·판매중지 1건 |
| `/api/weather/seoul` | 네비게이션 서울 날씨 |
| `/api/sanctions/latest` | 행정처분 |
| `/api/food-stats/yearly` | 식중독 통계 |

**FastAPI 백엔드가 필요한 경로** (Route Handler가 `BACKEND_URL`로 프록시):

| 경로 | 기능 |
|------|------|
| `/api/auth/*` | 로그인·회원가입·로그아웃 |
| `/api/mypage/*` | 마이페이지·리포트·프로필 |

로그인이 로컬에서만 되고 **foodopenlab.com에서 실패**하면, 대부분 `BACKEND_URL` 미설정 또는 `/api/auth/login` 404(구버전 배포)입니다. 아래 `BACKEND_URL` 설정 후 **Redeploy** 하세요.

## Vercel 환경 변수 (Production)

| 변수 | 필수 | 설명 |
|------|------|------|
| `GEMINI_API_KEY` | ✅ | Google AI Studio 키 (채팅 3종) |
| `FOOD_SAFETY_API_KEY` | 권장 | 식품안전나라 Open API (회수 목록·식품유형, **DB 없이 동작**) |
| `WEATHER_API_KEY` | 권장 | OpenWeatherMap (`/api/weather/seoul`) — **Production·Preview 모두**에 설정 권장 |
| `HACCP_PRODUCT_API_KEY` | 권장 | 식중독 통계(data.go.kr), 키 없으면 폴백 데이터 |
| `LAW_API_KEY` | 법규 채팅 | 법제처 OC 인증키 (`regulation-chat` 법령 검색) |
| `BACKEND_URL` | 로그인·마이페이지 | 공개 FastAPI HTTPS URL (예: `https://api.foodopenlab.com`) — **Neon DB와 동일한 프로덕션 DB** 연결 필수 |

**삭제 권장**

- `BACKEND_URL=https://www.foodopenlab.com` (프론트 도메인)
- `BACKEND_URL` = ngrok / localtunnel URL
- `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`

공개 FastAPI 서버를 별도로 운영할 때만:

```env
BACKEND_URL=https://api.실제백엔드도메인.com
```

변경 후 **Redeploy** 필수.

## 회수 목록이 1건만 보일 때

- `BACKEND_URL`이 켜져 있으면 예전에는 **빈 DB 백엔드** 응답이 우선될 수 있었습니다. 지금은 `/api/recalls*` 가 Vercel에서 **식품안전나라 API를 직접** 호출합니다.
- `FOOD_SAFETY_API_KEY` 설정 후에도 예전 배포가 돌아가면 스냅샷 1건만 보입니다 → **최신 커밋으로 Redeploy**.
- `WEATHER_API_KEY`를 **Production만** 넣으면 Preview URL에서는 날씨가 안 나옵니다. 사용하는 환경(Production / Preview)에 맞게 키를 추가하세요.

## Gemini 모델 (코드 기본값)

- 빠른 모델: `gemini-2.5-flash-lite`
- 선택: `gemini-3.1-flash-lite`

## 로컬 개발

`frontend/.env.local`:

```env
GEMINI_API_KEY=...
FOOD_SAFETY_API_KEY=...
HACCP_PRODUCT_API_KEY=...
LAW_API_KEY=...
BACKEND_URL=http://127.0.0.1:8000
```

백엔드: `uvicorn main:app --host 127.0.0.1 --port 8000 --reload --app-dir apps`

로컬에서는 `BACKEND_URL`이 있으면 나머지 API는 FastAPI로 rewrite되고, 없으면 Next API 라우트가 동작합니다.
