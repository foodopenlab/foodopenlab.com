# 서버 이전 런북 (Multi-project 공존)

> 목적: 이 프로젝트를 **다른 프로젝트가 이미 돌고 있는 우분투 서버**로 이전한다.
> 기존 서버 관례(**디렉토리 분리 + 컨테이너명 접두어 + 호스트 포트 오프셋**)에 맞춰 충돌 없이 나란히 배치한다.

## 충돌 회피 규칙

전역 네임스페이스에서 실제로 충돌하는 것은 **`container_name`** 과 **호스트 포트** 둘뿐이다.
서비스명(pgvector/redis/graph_db/korean_law_mcp)과 컨테이너 내부 포트는 프로젝트 네트워크 안에서만
유효하므로 변경하지 않는다 → **`backend/.env` 는 수정 불필요.**

| 서비스 | container_name | 호스트포트(외부:내부) |
|---|---|---|
| pgvector | `foodopenlab_pgvector` | `15432:5432` |
| redis | `foodopenlab_redis` | `16379:6379` |
| graph_db | `foodopenlab_graph_db` | `17474:7474`, `17687:7687` |
| korean_law_mcp | `foodopenlab_korean_law_mcp` | `13100:3100` |
| backend | `foodopenlab_fastapi_backend` | `18000:8000` |
| cloudflared | `foodopenlab_cloudflared` | (포트 없음, 터널) |

- 접두어: `foodopenlab_`
- 포트: 기존 기본포트 + 10000 오프셋
- compose 프로젝트명 고정: `-p foodopenlab` → 볼륨/네트워크가 `foodopenlab_*` 로 생성되어 분리됨
- 반영 파일: `docker-compose.server.yml`, `docker/foodopenlab-stack.server.service`

---

## 0) 새 서버 사전 준비

```bash
sudo apt update && sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER   # 재로그인
# GPU 예약(nvidia)을 쓰므로 드라이버 + nvidia-container-toolkit 필요.
#   GPU 없는 서버면 compose의 backend > deploy.resources 블록을 삭제.
```

## 1) 현재 서버에서 덤프 + 전송

```bash
cd /home/kcs88/projects/com.foodopenlab

# Postgres
docker cp $(docker ps -qf name=pgvector | head -1):/tmp/fol.dump ./fol_pg.dump 2>/dev/null || true
docker exec $(docker ps -qf name=pgvector | head -1) pg_dump -U pguser -d foodopenlab -Fc -f /tmp/fol.dump
docker cp $(docker ps -qf name=pgvector | head -1):/tmp/fol.dump ./fol_pg.dump

# Neo4j (오프라인 덤프 — 잠깐 정지)
docker stop $(docker ps -qf name=graph_db)
docker run --rm --volumes-from $(docker ps -aqf name=graph_db | head -1) \
  -v $(pwd):/backup neo4j:5.18-community \
  neo4j-admin database dump neo4j --to-path=/backup
docker start $(docker ps -aqf name=graph_db | head -1)

# 새 서버로 전송 (.env 는 git에 없으니 반드시 함께)
scp fol_pg.dump neo4j.dump .env backend/.env <user>@<new-server>:~/transfer/
```

> Redis 는 캐시/큐라 보통 이전 불필요. 필요 시 `dump.rdb` 를 별도 복사.

## 2) 새 서버에 소스 배치 + env 복원

```bash
git clone <repo> ~/projects/com.foodopenlab      # 또는 rsync
cd ~/projects/com.foodopenlab
cp ~/transfer/.env ./.env
cp ~/transfer/backend/.env ./backend/.env
# docker/foodopenlab-stack.server.service 의 WorkingDirectory 를 이 실제 경로로 수정
```

## 3) 스택 기동 (빈 DB 생성)

```bash
docker compose -p foodopenlab -f docker-compose.server.yml up -d
```

## 4) 데이터 복원

```bash
# Postgres
docker cp ~/transfer/fol_pg.dump foodopenlab_pgvector:/tmp/fol.dump
docker exec foodopenlab_pgvector pg_restore -U pguser -d foodopenlab --clean --if-exists /tmp/fol.dump

# Neo4j (정지 → load → 기동)
docker compose -p foodopenlab -f docker-compose.server.yml stop graph_db
docker run --rm --volumes-from foodopenlab_graph_db -v ~/transfer:/backup neo4j:5.18-community \
  neo4j-admin database load neo4j --from-path=/backup --overwrite-destination=true
docker compose -p foodopenlab -f docker-compose.server.yml start graph_db
```

## 5) 확인 + 서비스 등록

```bash
docker compose -p foodopenlab -f docker-compose.server.yml ps
curl -s localhost:18000/          # 백엔드 확인
sudo cp docker/foodopenlab-stack.server.service /etc/systemd/system/
sudo systemctl daemon-reload && sudo systemctl enable --now foodopenlab-stack.server
```

---

## 컷오버 주의사항

1. **Cloudflare 터널**: 토큰이 같으면 새 서버 cloudflared 가 커넥터로 등록된다. 터널 ingress 설정이
   `http://backend:8000`(서비스명) 이면 그대로 동작(서비스명 미변경). 확인 후 **옛 서버 cloudflared 를 정지**해
   트래픽을 새 서버로 넘긴다. 컷오버 순간 양쪽이 붙어 라운드로빈될 수 있음.
2. **NEO4J_PASSWORD**: 루트 `.env` 와 `backend/.env` 의 값이 동일해야 함(복사 후 재확인).
3. **호스트 포트 직접 접속 도구**: `:5432`, `:8000` → `:15432`, `:18000` 로 변경. 터널 경유 외부 트래픽은 영향 없음.
