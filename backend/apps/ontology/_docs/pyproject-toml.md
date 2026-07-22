# A2A Portfolio — Claude Code 하네스

온프렘 우분투(EXAONE 7.8B + BGE-M3) ↔ AWS 오케스트레이터(GPU 없음)를 **A2A**로 잇고,
그래프 DB를 **MCP 서버**로 감싸 에이전트가 도구처럼 질의하는 개인 포트폴리오 프로젝트다.
결과는 Vercel 프론트엔드로 표시한다.

이 문서를 Claude Code에 그대로 넘기면 저장소를 스캐폴딩할 수 있도록 작성했다.
아래 코드 블록 상단의 경로 주석이 곧 생성할 파일 경로다.

---

## 0. 스택 결정 (요약)

| 항목 | 선택 | 이유 |
|---|---|---|
| 패키지 매니저 | **uv** (워크스페이스) | 모노레포 다중 서비스 관리가 깔끔 |
| Python | **3.11** | mcp/a2a-sdk가 3.10+ 요구, 3.11이 안정적 |
| 빌드 백엔드 | **hatchling** | uv와 궁합 좋음 |
| A2A | **`a2a-sdk>=1.1,<2`** | v1.0 스펙 안정판 (Linux Foundation) |
| MCP | **`mcp[cli]>=1.27,<2`** | v2는 아직 프리릴리스 → v1 핀 |
| LLM 서빙 | **Ollama** (`ollama` 클라이언트) | EXAONE GGUF를 llama.cpp 컴파일 없이 구동 |
| 임베딩 | **sentence-transformers** (BGE-M3) | 표준. sparse/ColBERT 필요 시 FlagEmbedding |
| 그래프 DB | **Neo4j** (`neo4j` 드라이버) | MCP 서버로 래핑 |
| 프론트엔드 | Next.js on Vercel | Python 아님 → `web/`에 별도, pyproject 밖 |

> GPU 배분: EXAONE는 GPU(Q4_K_M, 약 5.5GB), BGE-M3는 CPU 권장(약 2GB).
> 3060 Ti 8GB에서 둘 다 GPU에 올리면 OOM 위험 → 기본값은 BGE-M3 CPU.

---

## 1. 디렉터리 구조

```
a2a-portfolio/
├── pyproject.toml              # 워크스페이스 루트 + dev 툴체인 + torch 인덱스
├── README.md
├── CLAUDE.md                   # Claude Code용 작업 지침/가드레일
├── .env.example
├── docker-compose.yml          # Neo4j (+ 서비스) 로컬 구동
├── packages/
│   └── common/                 # 공유 설정/모델/프로토콜 헬퍼
│       ├── pyproject.toml
│       └── src/common/
│           ├── __init__.py
│           ├── config.py
│           └── schemas.py
└── services/
    ├── onprem_agent/           # EXAONE + BGE-M3 · A2A 서버 · MCP 클라이언트
    │   ├── pyproject.toml
    │   └── src/onprem_agent/
    │       ├── __init__.py
    │       ├── __main__.py
    │       ├── agent.py         # A2A AgentExecutor (작업 처리)
    │       ├── llm.py           # Ollama(EXAONE) 래퍼
    │       ├── embeddings.py    # BGE-M3 (CPU)
    │       └── graph_client.py  # graph_mcp MCP 서버에 붙는 클라이언트
    ├── aws_orchestrator/        # A2A 오케스트레이터 (GPU 없음)
    │   ├── pyproject.toml
    │   └── src/aws_orchestrator/
    │       ├── __init__.py
    │       ├── __main__.py
    │       ├── api.py           # Vercel가 호출하는 얇은 HTTP 엔드포인트
    │       └── router.py        # onprem A2A 에이전트로 작업 위임
    └── graph_mcp/              # Neo4j를 감싼 MCP 서버
        ├── pyproject.toml
        └── src/graph_mcp/
            ├── __init__.py
            └── server.py        # FastMCP 툴: query / upsert_node / neighbors
```

---

## 2. 루트 `pyproject.toml`

```toml
# path: pyproject.toml
[project]
name = "a2a-portfolio"
version = "0.1.0"
description = "On-prem EXAONE + BGE-M3 agents talking to an AWS orchestrator via A2A, with a Neo4j graph exposed over MCP."
requires-python = ">=3.11"
readme = "README.md"

# 루트는 빌드 대상이 아니라 워크스페이스 오케스트레이션 전용
[tool.uv]
package = false

[tool.uv.workspace]
members = ["packages/*", "services/*"]

# --- 워크스페이스 공통 소스 ---------------------------------------------------
# torch는 CUDA 휠을 PyTorch 인덱스에서 받는다 (3060 Ti = Ampere → cu124 OK).
# CPU만 테스트할 때는 아래 url을 .../whl/cpu 로 바꾼다.
[[tool.uv.index]]
name = "pytorch-cu124"
url = "https://download.pytorch.org/whl/cu124"
explicit = true

[tool.uv.sources]
torch = { index = "pytorch-cu124" }

# --- 개발 도구 ----------------------------------------------------------------
[dependency-groups]
dev = [
    "ruff>=0.7",
    "mypy>=1.11",
    "pytest>=8.3",
    "pytest-asyncio>=0.24",
    "pre-commit>=4.0",
]

[tool.ruff]
line-length = 100
target-version = "py311"

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "ASYNC"]

[tool.mypy]
python_version = "3.11"
strict = true
plugins = ["pydantic.mypy"]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["services", "packages"]
```

---

## 3. `packages/common` — 공유 코드

```toml
# path: packages/common/pyproject.toml
[project]
name = "common"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "pydantic>=2.9",
    "pydantic-settings>=2.5",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/common"]
```

```python
# path: packages/common/src/common/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """모든 서비스가 공유하는 환경 설정. .env 에서 로드된다."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # LLM (Ollama / EXAONE)
    ollama_host: str = "http://localhost:11434"
    exaone_model: str = "exaone3.5:7.8b"

    # 임베딩 (BGE-M3)
    bge_model: str = "BAAI/bge-m3"
    bge_device: str = "cpu"  # 3060 Ti 8GB → BGE는 CPU 권장

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "please-change-me"

    # 서비스 주소
    onprem_agent_url: str = "http://localhost:9100"   # A2A 서버 (온프렘)
    orchestrator_port: int = 8000                      # Vercel가 호출
    graph_mcp_cmd: str = "graph-mcp"                   # MCP stdio 실행 커맨드


settings = Settings()
```

```python
# path: packages/common/src/common/schemas.py
from pydantic import BaseModel


class RetrieveRequest(BaseModel):
    query: str
    top_k: int = 5


class RetrievedNode(BaseModel):
    id: str
    text: str
    score: float


class AnswerResult(BaseModel):
    answer: str
    sources: list[RetrievedNode]
```

---

## 4. `services/onprem_agent` — EXAONE + BGE-M3 (A2A 서버)

```toml
# path: services/onprem_agent/pyproject.toml
[project]
name = "onprem-agent"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "common",
    "a2a-sdk>=1.1,<2",
    "mcp[cli]>=1.27,<2",           # MCP 클라이언트로 graph_mcp에 붙는다
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "httpx>=0.27",
    "pydantic>=2.9",
    "ollama>=0.4",                 # EXAONE 추론 (Ollama 서버 필요)
    "sentence-transformers>=3.3",  # BGE-M3
    "torch>=2.4",                  # CUDA 휠은 루트 인덱스에서 해결
]

[project.optional-dependencies]
# dense 외에 sparse/ColBERT 멀티벡터가 필요하면 설치
sparse = ["FlagEmbedding>=1.3"]

[project.scripts]
onprem-agent = "onprem_agent.__main__:main"

[tool.uv.sources]
common = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/onprem_agent"]
```

```python
# path: services/onprem_agent/src/onprem_agent/llm.py
import ollama

from common.config import settings


class ExaoneClient:
    """Ollama 서버에 올라간 EXAONE 7.8B 래퍼 (GPU 추론)."""

    def __init__(self) -> None:
        self._client = ollama.AsyncClient(host=settings.ollama_host)

    async def generate(self, prompt: str, context: str) -> str:
        resp = await self._client.chat(
            model=settings.exaone_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Answer using the context."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {prompt}"},
            ],
        )
        return resp["message"]["content"]
```

```python
# path: services/onprem_agent/src/onprem_agent/embeddings.py
from sentence_transformers import SentenceTransformer

from common.config import settings


class BgeEmbedder:
    """BGE-M3 임베딩. 기본 device=cpu (VRAM은 EXAONE에 양보)."""

    def __init__(self) -> None:
        self._model = SentenceTransformer(settings.bge_model, device=settings.bge_device)

    def encode(self, texts: list[str]) -> list[list[float]]:
        return self._model.encode(texts, normalize_embeddings=True).tolist()
```

> **`agent.py`**(A2A `AgentExecutor` 구현)와 **`graph_client.py`**(MCP stdio 클라이언트로
> `graph_mcp`의 `query`/`neighbors` 툴 호출)는 Claude Code가 구현한다.
> A2A 서버는 `a2a-sdk`의 `A2AStarletteApplication` + `DefaultRequestHandler` 패턴을 따르고,
> AgentCard의 skill은 `retrieve_and_answer` 하나로 시작한다.

```python
# path: services/onprem_agent/src/onprem_agent/__main__.py
import uvicorn

from common.config import settings


def main() -> None:
    # 실제 app 객체는 agent.py 에서 build_app()으로 노출한다.
    uvicorn.run(
        "onprem_agent.agent:build_app",
        factory=True,
        host="0.0.0.0",
        port=int(settings.onprem_agent_url.rsplit(":", 1)[-1]),
    )


if __name__ == "__main__":
    main()
```

---

## 5. `services/aws_orchestrator` — 오케스트레이터 (GPU 없음)

torch·임베딩 의존성이 전혀 없다. 라우팅/위임만 하므로 t4g.small·Lambda 수준에서 저렴하게 돈다.

```toml
# path: services/aws_orchestrator/pyproject.toml
[project]
name = "aws-orchestrator"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "common",
    "a2a-sdk>=1.1,<2",        # onprem A2A 에이전트에 작업 위임
    "fastapi>=0.115",
    "uvicorn[standard]>=0.32",
    "httpx>=0.27",
    "pydantic>=2.9",
]

[project.optional-dependencies]
aws = ["boto3>=1.35"]        # 필요 시 (SQS/Secrets 등)

[project.scripts]
aws-orchestrator = "aws_orchestrator.__main__:main"

[tool.uv.sources]
common = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/aws_orchestrator"]
```

```python
# path: services/aws_orchestrator/src/aws_orchestrator/api.py
from fastapi import FastAPI

from common.schemas import AnswerResult, RetrieveRequest

app = FastAPI(title="AWS Orchestrator")


@app.post("/ask", response_model=AnswerResult)
async def ask(req: RetrieveRequest) -> AnswerResult:
    # router.delegate_to_onprem(req) 가 A2A로 온프렘 에이전트를 호출한다.
    from aws_orchestrator.router import delegate_to_onprem

    return await delegate_to_onprem(req)
```

> **`router.py`**: `a2a-sdk`의 `A2AClient`로 `settings.onprem_agent_url`의 AgentCard를
> 조회한 뒤 task를 전송하고 결과를 `AnswerResult`로 매핑한다. (Claude Code 구현)

---

## 6. `services/graph_mcp` — Neo4j를 감싼 MCP 서버

```toml
# path: services/graph_mcp/pyproject.toml
[project]
name = "graph-mcp"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
    "common",
    "mcp[cli]>=1.27,<2",
    "neo4j>=5.20",
    "pydantic>=2.9",
]

[project.scripts]
graph-mcp = "graph_mcp.server:main"

[tool.uv.sources]
common = { workspace = true }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/graph_mcp"]
```

```python
# path: services/graph_mcp/src/graph_mcp/server.py
from mcp.server.fastmcp import FastMCP
from neo4j import GraphDatabase

from common.config import settings

mcp = FastMCP("graph-mcp")
_driver = GraphDatabase.driver(
    settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password)
)


@mcp.tool()
def query(cypher: str, params: dict | None = None) -> list[dict]:
    """읽기 전용 Cypher를 실행하고 레코드를 반환한다."""
    with _driver.session() as session:
        return [r.data() for r in session.run(cypher, params or {})]


@mcp.tool()
def neighbors(node_id: str, limit: int = 10) -> list[dict]:
    """주어진 노드의 이웃을 반환한다."""
    cypher = (
        "MATCH (n {id: $id})-[r]-(m) RETURN m, type(r) AS rel LIMIT $limit"
    )
    with _driver.session() as session:
        return [r.data() for r in session.run(cypher, {"id": node_id, "limit": limit})]


def main() -> None:
    mcp.run(transport="stdio")  # onprem_agent가 stdio로 이 서버를 띄워 붙는다


if __name__ == "__main__":
    main()
```

---

## 7. 인프라 파일

```yaml
# path: docker-compose.yml
services:
  neo4j:
    image: neo4j:5.24
    ports:
      - "7474:7474"   # 브라우저 UI
      - "7687:7687"   # bolt
    environment:
      NEO4J_AUTH: "neo4j/please-change-me"
    volumes:
      - neo4j_data:/data

volumes:
  neo4j_data:
```

```bash
# path: .env.example
OLLAMA_HOST=http://localhost:11434
EXAONE_MODEL=exaone3.5:7.8b
BGE_MODEL=BAAI/bge-m3
BGE_DEVICE=cpu

NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=please-change-me

ONPREM_AGENT_URL=http://localhost:9100
ORCHESTRATOR_PORT=8000
GRAPH_MCP_CMD=graph-mcp
```

---

## 8. 셋업 & 실행

```bash
# 0) uv 설치돼 있다고 가정. 워크스페이스 전체 동기화
uv sync

# 1) Ollama에 EXAONE 받기 (온프렘, GPU)
ollama pull exaone3.5:7.8b

# 2) Neo4j 띄우기
docker compose up -d neo4j

# 3) 그래프 MCP 서버 (stdio라 보통 onprem_agent가 자식 프로세스로 실행)
uv run graph-mcp

# 4) 온프렘 A2A 에이전트 (EXAONE + BGE-M3)
uv run onprem-agent

# 5) AWS 오케스트레이터 (다른 호스트/인스턴스에서)
uv run aws-orchestrator

# 품질 게이트
uv run ruff check .
uv run mypy .
uv run pytest
```

**네트워킹 주의**: 온프렘은 보통 공유기 NAT 뒤에 있다. AWS→온프렘 직결이 안 되므로
Cloudflare Tunnel(무료)이나 Tailscale로 `ONPREM_AGENT_URL`을 외부에 노출하거나,
온프렘이 오케스트레이터를 폴링하는 구조로 바꾼다. Vercel은 서버리스 타임아웃이 있으니
LLM 스트리밍은 오케스트레이터의 스트리밍 엔드포인트에서 직접 받는다.

---

## 9. `CLAUDE.md` (저장소 루트에 함께 생성)

```markdown
# path: CLAUDE.md

## 프로젝트
온프렘(EXAONE 7.8B + BGE-M3) ↔ AWS 오케스트레이터를 A2A로 연결하고,
Neo4j 그래프를 MCP 서버로 노출하는 포트폴리오. uv 워크스페이스 모노레포.

## 빌드/검증 커맨드 (변경 후 반드시 실행)
- `uv sync`
- `uv run ruff check . && uv run mypy . && uv run pytest`

## 규칙 (가드레일)
- 의존성 추가는 각 서비스의 pyproject.toml에만. 루트는 dev 툴/워크스페이스 설정 전용.
- MCP는 `mcp>=1.27,<2`로 고정. v2(2.0.0bN) 프리릴리스로 올리지 말 것.
- A2A는 `a2a-sdk>=1.1,<2`.
- aws_orchestrator에는 torch/임베딩/GPU 의존성을 절대 추가하지 말 것 (경량·저비용 유지).
- BGE-M3 device 기본값은 cpu. 3060 Ti 8GB에서 EXAONE(GPU)와 동시 상주 시 OOM 방지.
- 비밀값은 .env에서만 읽고 커밋 금지.
- src 레이아웃 유지. 각 서비스는 `packages/common`을 워크스페이스 소스로 참조.

## 다음 구현 순서
1. graph_mcp.server 툴 3개 (query/neighbors/upsert_node) + 스모크 테스트
2. onprem_agent.graph_client (MCP stdio 클라이언트)
3. onprem_agent.agent (A2A AgentExecutor, skill=retrieve_and_answer)
4. aws_orchestrator.router (A2AClient로 위임) + /ask 엔드포인트
5. web/ (Next.js) — /ask 호출, 결과 렌더
```

---

## 10. 범위 밖 메모

- **`web/`** (Vercel 프론트엔드)는 Next.js/TypeScript라 이 pyproject 워크스페이스에 넣지 않는다.
  별도 `package.json`으로 관리하고 Vercel에 배포한다.
- BGE-M3의 sparse/ColBERT 멀티벡터가 필요하면 `uv sync --extra sparse`로 FlagEmbedding 추가.
- CPU 전용 환경에서 테스트하려면 루트 pyproject의 pytorch 인덱스 url을 `.../whl/cpu`로 교체.