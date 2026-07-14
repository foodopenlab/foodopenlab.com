# 작업 환경 이전 (Windows PC → 상시 Ubuntu 개발 서버)

> **목표 구조**: 우분투 서버 = 유일한 개발 머신(코드·env·DB·모델 전부 여기).
> 윈도우(집)·맥(밖)은 **SSH 클라이언트**일 뿐 — 소스/시크릿을 로컬에 두지 않음.
> 현재 Windows PC는 이전 완료 후 폐기 → 아래 것들을 **폐기 전에** 빼내야 함.

## 이전 대상 요약

| 항목 | clone로 오나 | 처리 |
|---|---|---|
| 커밋된 코드 | ✅ | clone (단, 폐기 전 미커밋분 push 필수 — §0) |
| env 3개 | ❌ | 수동 복사 (§2) |
| Cloudflare 터널 토큰 | ❌ | 루트 `.env`에 포함(§2) + SSH 접근 설정(§3) |
| DB 볼륨 데이터 | ❌ | 선택 (§4) |
| hf_cache 모델(~418MB) | ❌ | 선택, 없으면 재다운로드 (§5) |
| YOLO 가중치·데이터셋, data/ | ✅ | clone에 포함 |

---

## 🔴 0. (구 컴퓨터) clone 전에 commit & push

새 컴에서 clone하기 **전**, 지금 컴에서 아직 원격에 없는 변경을 올린다.
안 올리면 새 컴에는 존재하지 않는다.

```bash
git status                 # 수정/untracked 확인
git add -A
git commit -m "wip: move environment"
git push origin hi         # 현재 브랜치
```

체크: 아래가 모두 push됐는지 확인
- 수정된 tracked 파일 (docker-compose.yaml, alembic/env.py, vision_router.py 등)
- untracked 새 파일 (moneyball ORM 4개, core/matrix/grid_device_manager.py, alembic 마이그레이션)

---

## 🔧 우분투 사전 준비 (clone 전에 1회)

```bash
# 1) Docker + Compose plugin
sudo apt update && sudo apt install -y docker.io docker-compose-plugin git
sudo usermod -aG docker $USER   # 로그아웃/로그인 후 sudo 없이 docker 사용

# 2) GPU 쓸 경우 — NVIDIA Container Toolkit (compose가 nvidia runtime 요구)
#    드라이버(nvidia-smi 동작) 설치 후:
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker && sudo systemctl restart docker
```

> Windows의 Docker Desktop과 달리 우분투는 위 설치가 선행돼야 함.

## 🔴 1. (새 컴퓨터) 코드 clone

```bash
git clone https://github.com/foodopenlab/foodopenlab.com.git com.foodopenlab
cd com.foodopenlab
git checkout hi            # 작업 브랜치
```

> 폴더명을 반드시 `com.foodopenlab` 로 (repo 기본명 `foodopenlab.com` 아님).
> docker compose 프로젝트 접두어가 `comfoodopenlab_` 로 고정돼 볼륨 이름이 맞는다.

**git 인증 (우분투 — Windows GCM 없음):**
```bash
# PAT(Personal Access Token) 방식 — push 시 1회 입력 후 저장
git config --global credential.helper store
# 또는 SSH 키 등록 후 remote를 git@github.com:... 로 변경
```

---

## 🔴 2. Secret / env 파일 3개 (gitignore → clone 안 됨)

수동 복사. USB 또는 암호화 전송. **git·메신저 평문 전송 금지.**

| 파일 | 주요 내용 |
|---|---|
| `.env` (루트) | `CLOUDFLARE_TUNNEL_TOKEN`, `POSTGRES_PASSWORD`, `NEO4J_PASSWORD` |
| `backend/.env` | `DATABASE_URL`, `ADMIN_JWT_SECRET`, `GEMINI_API_KEY`, 정부 API 키(FOOD_SAFETY/HACCP/LAW/NCBI/SCIENCEON), n8n webhook |
| `frontend/.env.local` | `GEMINI_API_KEY`, `WEATHER_API_KEY` 등 |

> 주의: 루트 `.env`의 `NEO4J_PASSWORD` 는 `backend/.env` 값과 **동일**해야 함 (compose 변수 치환).

### clone에 안 딸려오지만 — 수동 이전 불필요 (참고)

아래는 gitignore라 clone엔 없지만, **자동 재생성되거나 개인 설정**이라 옮길 필요 없음.
(env 3개만 예외적으로 필수 — 위 표 참조)

| 항목 | 처리 | 비고 |
|---|---|---|
| `backend/*.pt` (yolo11n/26n/v8n 가중치 4개) | 🟢 자동 다운로드 | ultralytics가 첫 실행 시 받음. 커스텀 학습 모델은 없음(`runs/` 없음) |
| `pytorch_env/` (파이썬 venv) | 🟢 재생성 | `pip install -r ...` |
| `node_modules/`, `.next/` | 🟢 재생성 | `npm install` |
| `__pycache__/` 전부 | 🟢 무시 | 자동 생성 |
| `plan_flutter/android/local.properties` | 🟢 자동 | Flutter SDK 경로, 머신별 |
| `.vscode/`, `.obsidian/workspace.json` | ⚪ 선택 | 에디터/옵시디언 개인 레이아웃 |
| `frontend/app/admin/logs/` | ⚪ 무시 | 런타임 로그 |

> ✅ 걱정 안 해도 되는 것 (전부 git 추적됨 → clone에 딸려옴):
> YOLO 학습 데이터셋(train 93 + val 25장), `backend/data`·`frontend/data`·`mfds_user/data`.

---

## 🟡 3. SSH 원격 개발 접근 (윈도우/맥 → 서버)

서버는 공인 IP 없이 **Cloudflare 터널**로 SSH 노출 (`ssh.foodopenlab.com`).

**서버 측(우분투):**
- 백엔드 API 터널 토큰은 루트 `.env`의 `CLOUDFLARE_TUNNEL_TOKEN` 에 포함(§2).
- SSH용 터널은 Cloudflare Zero Trust 대시보드에서 `ssh.foodopenlab.com` → `ssh://localhost:22` 매핑 확인.
- `openssh-server` 설치: `sudo apt install -y openssh-server`.

**클라이언트 측(윈도우 집 / 맥 밖):** 각 기기에 `cloudflared` 설치 후 `~/.ssh/config`에:
```
Host foodopenlab
  HostName ssh.foodopenlab.com
  User <서버계정>
  ProxyCommand cloudflared access ssh --hostname %h
```
→ `ssh foodopenlab` 로 접속. VS Code/Cursor **Remote-SSH** 확장으로 이 Host를 열면 서버에서 직접 개발.

> 구 PC `~/.cloudflared/`의 토큰은 복사보다 **각 클라이언트에서 재발급**이 깔끔:
> `cloudflared access login ssh.foodopenlab.com`

---

## 🟡 4. Docker 볼륨 (DB 실제 데이터) — 선택

현재 볼륨:
`comfoodopenlab_pgvector_data`, `_redis_data`, `_neo4j_data`, `_neo4j_logs`, `n8n_data`(external)

**결정: 전부 유지 이전.** 구 PC에서 5개 볼륨 백업 완료(2026-07-14).

### 1) 구 PC 백업 (완료됨)
- 위치: `C:\Users\hi\Documents\foodopenlab_db_backup\`
- 파일: `comfoodopenlab_pgvector_data.tar.gz`(57M), `_neo4j_data.tar.gz`, `_neo4j_logs.tar.gz`, `_redis_data.tar.gz`, `n8n_data.tar.gz`
- **이 폴더를 통째로 서버로 전송** (USB 또는 `scp -r`).

### 2) 서버(우분투) 복원
```bash
# 컨테이너 아직 안 띄운 상태에서 (또는 docker compose down 후)
cd <백업폴더>          # tar.gz 5개가 있는 곳

for v in comfoodopenlab_pgvector_data comfoodopenlab_neo4j_data \
         comfoodopenlab_neo4j_logs comfoodopenlab_redis_data n8n_data; do
  docker volume create "$v"
  docker run --rm -v "$v":/data -v "$PWD":/backup \
    alpine tar xzf "/backup/$v.tar.gz" -C /data
done
```
> ⚠️ **폴더 이름이 `com.foodopenlab` 여야** compose가 이 볼륨(`comfoodopenlab_` 접두어)을 인식 (§1).
> ⚠️ Postgres/Neo4j **메이저 버전 동일**해야 복원 성공 — compose 이미지 태그 확인.
> `n8n_data` 는 `external: true` 라 위 `docker volume create` 로 반드시 선생성 (compose가 자동생성 안 함).
> 복원은 **`docker compose up` 전에** 완료할 것 (빈 볼륨이 먼저 생기면 안 됨).

---

## 🟢 5. HuggingFace 모델 캐시 경로 — compose 수정 완료

`docker-compose.yaml`의 `D:/hf_cache` 하드코딩을 환경변수 방식으로 **이미 교체함**:
```yaml
- ${HF_CACHE_DIR:-./hf_cache}:/hf_cache
```
- 우분투: `.env`에 `HF_CACHE_DIR=/opt/hf_cache` 설정, 또는 미설정 시 `./hf_cache` 기본값 사용.
- (구 Windows: `HF_CACHE_DIR=D:/hf_cache` 였음 — 폐기 예정이라 무관.)

캐시 데이터(~418MB) 자체는 **선택** — 없으면 첫 실행 시 자동 재다운로드.
옮기려면 구 PC `D:/hf_cache` 내용을 서버 경로(`/opt/hf_cache` 등)에 복사.

---

## ✅ 6. (새 컴퓨터) 기동 확인

```bash
docker compose up -d
docker compose ps          # 전 서비스 healthy 확인
# backend: http://localhost:8000  frontend: http://localhost:3000
```

- CORS: `backend/.env`의 `CORS_ORIGINS` 에 운영 오리진(`https://foodopenlab.com`) 포함 확인.
- GPU: `nvidia-smi` 동작 + NVIDIA Container Toolkit 설치 확인 (위 사전 준비). GPU 없으면 compose의 `deploy.resources.reservations` GPU 블록 제거 필요.
- hf_cache 경로 compose 수정은 이미 반영됨(§5). 서버 `.env`에 `HF_CACHE_DIR`만 확인.

---

## 브랜치 전략 재검토 (구조 변경으로 필요)

기존 "머신별 브랜치(server / hi / main)"는 **머신이 여러 대**일 때 전제.
이제 개발 머신은 **우분투 서버 1대**뿐 — 윈도우·맥은 SSH 클라이언트로 **같은 작업 트리 하나**를 공유.

→ 결정 필요:
- **(A) 단일 트리 공유**: 두 클라이언트가 서버의 같은 clone에서 작업. 브랜치는 기능별로만 운영. 가장 단순. **권장.**
- **(B) 클라이언트별 worktree**: `git worktree`로 윈도우용/맥용 분리 → 동시 작업 시 충돌 회피.

git author 설정은 **서버에서 1회**만: `git config user.name/user.email` (현재 `foodopenlab-com` / `kcs8815@gmail.com`).
