---
type: hub
domain: ontology
links:
  - titanic
  - siliconvalley
  - mfds_user
  - mfds_admin
  - imitation_game
  - inception
  - social_network
db:
  - graph_db
  - vector_db
---

# Star Craft Hub — Graph & Vector DB Pipeline 전략

> **위치:** `backend/apps/ontology/`  
> **역할:** 스타 토폴로지 허브 — 모든 Spoke의 지식이 교차하는 온톨로지 중심점  
> **목표:** Docker 내 `graph.db`(Neo4j) · `vector.db`(Qdrant)에 접속하는 파이프라인을 헥사고날 아키텍처로 구현한다.

---

## 1. 왜 Hub에 Graph + Vector DB인가

| DB | 역할 | Hub에서 하는 일 |
|----|------|----------------|
| **graph.db (Neo4j)** | 관계형 온톨로지 저장 | Spoke 간 연결 메타데이터, 엔티티 관계 그래프, 컨텍스트 라우팅 규칙 |
| **vector.db (Qdrant)** | 임베딩 시맨틱 검색 | Spoke 도메인별 지식 벡터화, RAG 파이프라인, 유사 컨텍스트 검색 |

두 DB를 동시에 쓰는 이유:  
- **그래프** = "누가 누구와 연결되어 있는가" (구조적 관계)  
- **벡터** = "어떤 내용이 유사한가" (의미론적 근접성)  
- Hub는 이 둘을 **결합 쿼리(Graph-RAG)**로 활용해 Spoke에 컨텍스트를 배포한다.

---

## 2. Docker 서비스 구성

### 추가할 서비스 (`docker-compose.yaml`)

```yaml
services:
  # --- 기존 서비스 (backend / frontend / n8n) 유지 ---

  graph_db:
    image: neo4j:5.18-community
    container_name: graph_db
    ports:
      - "7474:7474"   # Neo4j Browser
      - "7687:7687"   # Bolt protocol
    environment:
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}
      NEO4J_PLUGINS: '["apoc"]'
    volumes:
      - neo4j_data:/data
      - neo4j_logs:/logs
    healthcheck:
      test: ["CMD", "cypher-shell", "-u", "neo4j", "-p", "${NEO4J_PASSWORD}", "RETURN 1"]
      interval: 10s
      timeout: 5s
      retries: 5

  vector_db:
    image: qdrant/qdrant:v1.9.2
    container_name: vector_db
    ports:
      - "6333:6333"   # HTTP REST
      - "6334:6334"   # gRPC
    volumes:
      - qdrant_data:/qdrant/storage
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6333/healthz"]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  neo4j_data:
  neo4j_logs:
  qdrant_data:
  n8n_data:
    external: true
```

### 환경변수 (`.env` 추가)

```dotenv
# Graph DB (Neo4j)
NEO4J_URI=bolt://graph_db:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_secure_password

# Vector DB (Qdrant)
QDRANT_HOST=vector_db
QDRANT_PORT=6333
QDRANT_GRPC_PORT=6334

# Embedding model (Ollama 경유)
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_DIM=768
```

---

## 3. 헥사고날 파이프라인 설계

```
[Inbound] Router / MCP / Schedule
        ↓
[App]    OntologyUseCase (Interactor)
        ↓
[Port]   IGraphRepository (abstract)
         IVectorRepository (abstract)
        ↓
[Outbound Adapter]
   Neo4jRepository  →  graph_db:7687 (Bolt)
   QdrantRepository →  vector_db:6333 (HTTP/gRPC)
```

### 3-1. 포트 정의 (`app/ports/`)

```python
# app/ports/graph_port.py
from abc import ABC, abstractmethod
from ontology.app.dtos.graph_dto import NodeDTO, EdgeDTO, SubgraphDTO

class IGraphRepository(ABC):
    @abstractmethod
    async def upsert_node(self, node: NodeDTO) -> NodeDTO: ...

    @abstractmethod
    async def upsert_edge(self, edge: EdgeDTO) -> EdgeDTO: ...

    @abstractmethod
    async def get_subgraph(self, domain: str, depth: int = 2) -> SubgraphDTO: ...

    @abstractmethod
    async def find_path(self, from_domain: str, to_domain: str) -> list[str]: ...
```

```python
# app/ports/vector_port.py
from abc import ABC, abstractmethod
from ontology.app.dtos.vector_dto import VectorPointDTO, SearchResultDTO

class IVectorRepository(ABC):
    @abstractmethod
    async def upsert(self, collection: str, point: VectorPointDTO) -> None: ...

    @abstractmethod
    async def search(
        self,
        collection: str,
        query_vector: list[float],
        top_k: int = 5,
    ) -> list[SearchResultDTO]: ...

    @abstractmethod
    async def delete_collection(self, collection: str) -> None: ...
```

### 3-2. 아웃바운드 어댑터 (`adapter/outbound/repositories/`)

```python
# adapter/outbound/repositories/neo4j_repository.py
from neo4j import AsyncGraphDatabase
from ontology.app.ports.graph_port import IGraphRepository

class Neo4jRepository(IGraphRepository):
    def __init__(self, uri: str, user: str, password: str):
        self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def upsert_node(self, node: NodeDTO) -> NodeDTO:
        async with self._driver.session() as session:
            result = await session.run(
                "MERGE (n:Domain {id: $id}) SET n += $props RETURN n",
                id=node.id, props=node.props,
            )
            ...
```

```python
# adapter/outbound/repositories/qdrant_repository.py
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
from ontology.app.ports.vector_port import IVectorRepository

class QdrantRepository(IVectorRepository):
    def __init__(self, host: str, port: int):
        self._client = AsyncQdrantClient(host=host, port=port)

    async def upsert(self, collection: str, point: VectorPointDTO) -> None:
        await self._client.upsert(
            collection_name=collection,
            points=[PointStruct(id=point.id, vector=point.vector, payload=point.payload)],
        )
```

### 3-3. 의존성 주입 (`dependencies/`)

```python
# dependencies/__init__.py
from functools import lru_cache
from ontology.adapter.outbound.repositories.neo4j_repository import Neo4jRepository
from ontology.adapter.outbound.repositories.qdrant_repository import QdrantRepository
from ontology.app.use_cases.hub_use_case import HubInteractor
from core.matrix.config import settings

@lru_cache
def get_graph_repository() -> Neo4jRepository:
    return Neo4jRepository(
        uri=settings.NEO4J_URI,
        user=settings.NEO4J_USER,
        password=settings.NEO4J_PASSWORD,
    )

@lru_cache
def get_vector_repository() -> QdrantRepository:
    return QdrantRepository(
        host=settings.QDRANT_HOST,
        port=settings.QDRANT_PORT,
    )

def get_hub_use_case(
    graph_repo=Depends(get_graph_repository),
    vector_repo=Depends(get_vector_repository),
) -> HubInteractor:
    return HubInteractor(graph_repo=graph_repo, vector_repo=vector_repo)
```

---

## 4. 핵심 파이프라인 — Graph-RAG

Hub의 핵심 기능: **Spoke가 보낸 쿼리 → Graph 구조 탐색 → Vector 유사 검색 → 컨텍스트 반환**

```
Spoke Query
    │
    ▼
[1] Neo4j: 해당 Spoke 노드에서 관련 개념 서브그래프 추출
    │  (depth=2 관계, 온톨로지 태그)
    ▼
[2] subgraph → 임베딩 생성 (Ollama nomic-embed-text)
    │
    ▼
[3] Qdrant: 임베딩 벡터로 top-K 시맨틱 유사 컨텍스트 검색
    │
    ▼
[4] Graph 구조 + Vector 결과 병합 → 컨텍스트 패키지
    │
    ▼
Spoke에 컨텍스트 반환 (UseCase Output DTO)
```

### 유스케이스 스켈레톤

```python
# app/use_cases/hub_use_case.py
class HubInteractor:
    def __init__(self, graph_repo: IGraphRepository, vector_repo: IVectorRepository):
        self._graph = graph_repo
        self._vector = vector_repo

    async def route_context(self, query: ContextQueryDTO) -> ContextResponseDTO:
        # 1. Graph: 연관 서브그래프
        subgraph = await self._graph.get_subgraph(query.domain, depth=2)

        # 2. Embed subgraph summary (asyncio.to_thread → Ollama)
        embedding = await asyncio.to_thread(_embed, subgraph.summary)

        # 3. Vector: 시맨틱 유사 컨텍스트
        hits = await self._vector.search(
            collection=query.domain,
            query_vector=embedding,
            top_k=query.top_k,
        )

        return ContextResponseDTO(subgraph=subgraph, semantic_hits=hits)

    async def register_spoke(self, node: NodeDTO, documents: list[VectorPointDTO]) -> None:
        # Spoke 온보딩: Graph 노드 + Vector 컬렉션 동시 등록
        await self._graph.upsert_node(node)
        for doc in documents:
            await self._vector.upsert(collection=node.domain, point=doc)
```

---

## 5. 컬렉션 · 레이블 명명 규칙

### Neo4j 노드 레이블

| 레이블 | 의미 |
|--------|------|
| `Domain` | Spoke 앱 식별자 (`titanic`, `siliconvalley` ...) |
| `Concept` | 도메인 내 온톨로지 개념 |
| `Route` | Hub가 관리하는 라우팅 규칙 |

### Neo4j 관계 타입

| 관계 | 의미 |
|------|------|
| `CONNECTS_TO` | Spoke 간 허브 경유 연결 |
| `BELONGS_TO` | Concept → Domain |
| `ROUTES_VIA` | 컨텍스트 라우팅 경로 |

### Qdrant 컬렉션

| 컬렉션명 | 내용 |
|----------|------|
| `ontology_global` | Hub 전역 컨텍스트 |
| `{domain}_knowledge` | 각 Spoke 도메인 지식 (예: `titanic_knowledge`) |

---

## 6. 구현 순서 (단계별 검증)

| # | 작업 | 검증 기준 |
|---|------|----------|
| 1 | `docker-compose.yaml`에 `graph_db` · `vector_db` 서비스 추가 | `docker compose up -d graph_db vector_db` → 헬스체크 통과 |
| 2 | `.env`에 DB 환경변수 추가 | `settings.NEO4J_URI` 로드 확인 |
| 3 | `IGraphRepository` · `IVectorRepository` 포트 작성 | 추상 클래스 import 오류 없음 |
| 4 | `Neo4jRepository` 어댑터 구현 | `upsert_node` → Neo4j Browser에서 노드 확인 |
| 5 | `QdrantRepository` 어댑터 구현 | `upsert` → `GET /collections/{name}` 200 응답 |
| 6 | `HubInteractor` 유스케이스 구현 | `register_spoke` → Graph 노드 + Vector 컬렉션 동시 생성 |
| 7 | `dependencies/` DI 배선 | FastAPI `Depends` 체인 통과 |
| 8 | Inbound 라우터 엔드포인트 노출 | `POST /api/ontology/context` 200 |
| 9 | Spoke 온보딩 통합 테스트 | `titanic` → Hub 등록 → Graph+Vector 조회 성공 |

---

## 7. 의존성 패키지

```toml
# pyproject.toml 또는 requirements.txt 추가
neo4j = "^5.18"          # Python async driver
qdrant-client = "^1.9"   # Qdrant async client
httpx = "^0.27"          # HTTP (임베딩 API 호출)
```

---

## 8. 아키텍처 제약 재확인

- `ontology` 내 순환 참조 금지 (Hub 자체 내 circular import)
- `Neo4jRepository` · `QdrantRepository` 는 도메인 레이어를 import하지 않는다
- Spoke는 Hub의 포트(추상)만 참조 — 어댑터 구현체 직접 참조 금지
- 모든 DB I/O는 `async` — 블로킹 driver 사용 시 `asyncio.to_thread` 위임

---

_docs acknowledged: CLAUDE.md (monorepo) + backend/CLAUDE.md § Star Topology_
