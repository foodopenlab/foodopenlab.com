# pgAdmin — pgvector DB 관리 UI

Docker의 `pgvector`(PostgreSQL 17) 데이터베이스를 브라우저에서 조회·관리하기 위한 pgAdmin 설정.

## 접속

- **URL:** http://localhost:5050
- **로그인 계정** (`.env`의 `PGADMIN_DEFAULT_*`):
  - Email: `admin@foodopenlab.com`
  - Password: `E1nDzOyYVe7iqTNFLtf9`

## 서버 등록 (pgvector 연결)

로그인 후 좌측 트리에 `pgvector (foodopenlab)` 서버가 자동 등록되어 있다
(`docker/pgadmin/servers.json` 프리셋). 펼칠 때 DB 비밀번호를 1회 입력한다.

자동 등록이 안 보이면 **Register → Server**로 직접 등록한다.

### General 탭
| 항목 | 값 |
|---|---|
| Name | `pgvector (foodopenlab)` (임의 이름 가능) |

### Connection 탭 (핵심)
| 항목 | 값 |
|---|---|
| Host name/address | `pgvector` |
| Port | `5432` |
| Maintenance database | `foodopenlab` |
| Username | `pguser` |
| Password | `E1nDzOyYVe7iqTNFLtf9` |
| Save password? | ON |

> **Host는 반드시 `pgvector`** (Docker 컨테이너 이름). pgAdmin 컨테이너가 pgvector와
> 같은 네트워크에 있어 컨테이너 이름으로 접속된다. `localhost`/`127.0.0.1`을 넣으면
> pgAdmin 컨테이너 자신을 가리켜 실패한다.

나머지 탭(Parameters, SSH Tunnel, Advanced 등)은 기본값 그대로 둔다.

등록 후 `Databases > foodopenlab > Schemas > public > Tables`에서 테이블
(`users`, `law_chunks`, `agent_messages` 등)을 조회한다.

## Docker 구성

`docker-compose.yaml`의 `pgadmin` 서비스:

- 이미지: `dpage/pgadmin4:latest`
- 포트: `5050:80`
- 볼륨: `pgadmin_data`(설정 영속), `./docker/pgadmin/servers.json`(서버 프리셋, read-only)
- `PGADMIN_CONFIG_SERVER_MODE: "False"` — 단일 사용자 데스크톱 모드
- `depends_on: pgvector (service_healthy)`

### 실행 / 중지
```bash
docker compose up -d pgadmin      # 실행
docker compose restart pgadmin    # 재시작
docker compose stop pgadmin       # 중지
docker logs --tail 30 pgadmin     # 로그 확인
```

## 주의사항

- `PGADMIN_DEFAULT_EMAIL`은 **유효한 이메일 형식**이어야 한다. `.local` 등
  예약 도메인은 pgAdmin이 거부하여 컨테이너가 `Exited (1)`로 죽는다 → `.com` 사용.
- 로그인·DB 비밀번호는 `.env`에만 존재하며 `.env`는 gitignore 대상이다.
