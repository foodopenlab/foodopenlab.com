# System Prompt: 축구 ERD 기반 Alembic 마이그레이션 및 pgvector 테이블 생성 프롬프트

본 문서는 **카파시의 하네스 원칙(Harness Principle)**에 따라 설계된 구조화된 LLM 프롬프트입니다. 입력 하네스(스펙 정의), 엄격한 실행 지침, 컨텍스트 바운더리, 자체 검증/테스트 프로토콜을 제공하여 **Claude Code**가 Ubuntu 26.04 환경에서 `pgvector`가 활성화된 PostgreSQL용 Alembic 마이그레이션 코드를 완벽하게 생성하도록 유도합니다.

---

## [Task Objective / 작업 목표]
제공된 축구 데이터베이스 ERD 스키마를 기반으로 Python SQLAlchemy 모델 정의 및 Alembic 마이그레이션 스크립트(env.py 설정 고려 사항 및 마이그레이션 리비전 파일)를 작성합니다. 이때 선수 정보, 구장/팀 특성 등에 대한 시맨틱 검색(유사도 검색)이 가능하도록 `pgvector` 확장을 테이블 설계 내에 완벽하게 통합해야 합니다.

## [System & Environment Context / 시스템 환경]
- **OS**: Ubuntu 26.04 LTS
- **Database**: PostgreSQL (내부에 `pgvector` 익스텐션이 설치 및 활성화된 상태)
- **ORM / Migration**: SQLAlchemy 2.0+ 및 Alembic 1.13+
- **Vector Python 라이브러리**: `pgvector-python` (`from pgvector.sqlalchemy import Vector`)

---

## [The Input Harness: ERD 명세 및 메타데이터]

### 1. 테이블: `stadium`
- `stadium_id`: VARCHAR(10), Primary Key
- `statdium_name`: VARCHAR(40), Not Null (주의: ERD의 철자 오타인 'statdium_name'을 그대로 유지할 것)
- `hometeam_id`: VARCHAR(10)
- `seat_count`: INTEGER
- `address`: VARCHAR(60)
- `ddd`: VARCHAR(10)
- `tel`: VARCHAR(10)
- *벡터 확장 옵션*: 구장 편의시설이나 구조적 특징을 시맨틱 검색하기 위해 `stadium_embedding` Vector(1536) 컬럼 추가.

### 2. 테이블: `team`
- `team_id`: VARCHAR(10), Primary Key
- `region_name`: VARCHAR(10)
- `team_name`: VARCHAR(40), Not Null
- `e_team_name`: VARCHAR(50)
- `orig_yyyy`: VARCHAR(10)
- `zip_code1`: VARCHAR(10)
- `zip_code2`: VARCHAR(10)
- `address`: VARCHAR(80)
- `ddd`: VARCHAR(10)
- `tel`: VARCHAR(10)
- `fax`: VARCHAR(10)
- `homepage`: VARCHAR(50)
- `owner`: VARCHAR(10)
- `stadium_id`: VARCHAR(10), Foreign Key -> `stadium.stadium_id` 참조
- *벡터 확장 옵션*: 팀의 전술 프로필이나 히스토리를 시맨틱 검색하기 위해 `team_strategy_embedding` Vector(1536) 컬럼 추가.

### 3. 테이블: `schedule`
- 복합 기본키 (Composite Primary Key): (`sche_date`, `stadium_id`)
- `sche_date`: VARCHAR(10)
- `stadium_id`: VARCHAR(10), Foreign Key -> `stadium.stadium_id` 참조
- `gubun`: VARCHAR(10)
- `hometeam_id`: VARCHAR(10)
- `awayteam_id`: VARCHAR(10)
- `home_score`: INTEGER
- `away_score`: INTEGER
- *벡터 확장 옵션*: 경기 요약, 매치 리포트, 경기 흐름 등을 시맨틱 검색하기 위해 `match_summary_embedding` Vector(1536) 컬럼 추가.

### 4. 테이블: `player`
- `player_id`: VARCHAR(10), Primary Key
- `player_name`: VARCHAR(20), Not Null
- `e_player_name`: VARCHAR(40)
- `nickname`: VARCHAR(30)
- `join_yyyy`: VARCHAR(10)
- `position`: VARCHAR(10)
- `back_no`: INTEGER
- `nation`: VARCHAR(20)
- `birth_date`: DATE
- `solar`: VARCHAR(10)
- `height`: INTEGER
- `weight`: INTEGER
- `team_id`: VARCHAR(10), Foreign Key -> `team.team_id` 참조
- *벡터 확장 필수 요구사항*: 선수의 스카우트 리포트, 플레이 스타일, 텍스트 설명을 기반으로 시맨틱 유사도 검색을 수행하기 위해 `player_profile_embedding` Vector(1536) 컬럼 필수 추가.

---

## [Strict Execution & Coding Constraints / 제약 조건]

1. **pgvector 연동 규칙**:
   - 마이그레이션 리비전 파일의 `upgrade()` 메서드 내에서, 벡터 컬럼을 사용하는 테이블을 생성하기 **직전**에 반드시 `op.execute("CREATE EXTENSION IF NOT EXISTS vector;")` 명령을 실행하도록 코드를 작성해야 합니다.
   - 벡터 필드는 `pgvector.sqlalchemy.Vector(1536)` 형태로 정의합니다 (OpenAI의 `text-embedding-3-small` 표준 규격으로 가정하되 차원 수는 조절 가능하도록 설계).

2. **Alembic 지시어 사용**:
   - 일반 텍스트 쿼리로 테이블을 생성하지 말고, Alembic 고유의 `op.create_table` 구조를 완벽히 준수하십시오.
   - ERD에 표시된 모든 외래키 관계(`op.create_foreign_key`)를 엄격하게 매핑하십시오.
   - `schedule` 테이블의 복합 PK 제약조건이 누락되지 않도록 선언하십시오.

3. **데이터 무결성 및 명명 규칙**:
   - ERD 상의 Null/Not Null 제약조건 및 문자열 길이(예: `VARCHAR(10)`, `VARCHAR(40)`)를 소스 코드 내에 정확히 반영하십시오.

---

## [Self-Verification & Test Harness Protocol / 자체 검증 프로토콜]

하네스 원칙을 충족하기 위해, 생성되는 출력 코드 블록 내부에는 마이그레이션이 성공적으로 수행되었는지 확인하는 **검증 스크립트(Verification Script)**를 반드시 포함해야 합니다:
1. **익스텐션 활성화 확인**: 데이터베이스에 `SELECT * FROM pg_extension WHERE extname = 'vector';` 쿼리를 실행하여 익스텐션이 정상 등록되었는지 검증하는 절차.
2. **벡터 차원 검증**: 1536개 요소를 가진 부동소수점 배열이 데이터 타입 불일치 에러 없이 `player_profile_embedding` 컬럼에 정상적으로 INSERT/COMMIT 되는지 확인하는 테스트 코드 스니펫.
3. **인덱스 생성 제안**: Ubuntu 26.04 운영 환경에서 대량의 벡터 검색 성능을 보장하기 위해 HNSW 또는 IVFFlat 인덱스를 생성하는 DDL/SQLAlchemy 구문을 함께 제시할 것.

---

## [Expected Output Format / 기대하는 출력 포맷]
답변은 아래 구조에 맞추어 명확하게 출력되어야 합니다:
1. **SQLAlchemy 모델 파일 (`models.py`)**: `Vector` 타입을 포함하는 ORM 선언형 모델 코드.
2. **Alembic 마이그레이션 스크립트 (`xxxx_migration_name.py`)**: `upgrade()` 및 `downgrade()` 함수가 완벽히 작성된 리비전 파일 코드.
3. **검증 스니펫 (Verification Snippet)**: 데이터베이스 계층에서 성공 여부를 즉시 테스트할 수 있는 파이썬 또는 Raw SQL 코드 블록.



# System Prompt: Ubuntu 26.04 기반 pgvector PostgreSQL Docker 컨테이너 구축 프롬프트

본 문서는 **카파시의 하네스 원칙(Harness Principle)**에 따라 설계된 구조화된 LLM 프롬프트입니다. 입력 하네스(도커 스펙 정의), 엄격한 실행 지침, 컨텍스트 바운더리, 자체 검증/테스트 프로토콜을 제공하여 **Claude Code**가 Ubuntu 26.04 호스트 환경에서 `pgvector`가 완벽히 구성된 PostgreSQL 도커 환경(Dockerfile 및 docker-compose.yml)을 안전하게 자동 생성하도록 유도합니다.

---

## [Task Objective / 작업 목표]
제공된 축구 ERD 기반 Alembic 마이그레이션이 정상적으로 수행될 수 있도록, `pgvector` 익스텐션이 설치 및 컴파일된 PostgreSQL 데이터베이스를 Docker 컨테이너 환경으로 빌드하고 구동하는 코드를 작성합니다. 운영 환경 사양에 맞춘 인덱스 최적화 설정도 반영되어야 합니다.

## [System & Environment Context / 시스템 환경]
- **Host OS**: Ubuntu 26.04 LTS
- **Base Docker Image**: `postgres:16-alpine` 또는 `postgres:16` (안정성 및 경량화 기준)
- **Database**: PostgreSQL 16 + `pgvector` v0.5.0+ (소스 빌드 또는 공식 확장 패키지 이용)
- **Target Target Ports**: `5432:5432`

---

## [The Input Harness: Docker 환경 스펙 명세]

### 1. Dockerfile 구성 스펙
- **멀티 스테이지 빌드 또는 의존성 설치**: pgvector 컴파일을 위해 `build-base`, `git`, `postgresql-dev` (alpine 기준) 또는 `build-essential`, `postgresql-server-dev-16`, `git` (debian base 기준) 패키지를 임시 설치하여 빌드할 것.
- **pgvector 소스 다운로드 및 설치**: `https://github.com/pgvector/pgvector.git` 리포지토리를 클론하여 최신 안정 버전을 `make && make install` 구조로 빌드.
- **최적화**: 이미지 용량 최소화를 위해 빌드 직후 컴파일 의존성 패키지는 즉시 삭제 런타임 레이어 유지.

### 2. docker-compose.yml 구성 스펙
- **서비스명**: `db`
- **컨테이너명**: `moneyball-postgres-vector`
- **볼륨 바인딩 (데이터 영속성)**: 호스트의 볼륨 공간과 컨테이너 내부의 `/var/lib/postgresql/data` 매핑.
- **환경 변수**: 
  - `POSTGRES_DB`: `moneyball`
  - `POSTGRES_USER`: `balladmin`
  - `POSTGRES_PASSWORD`: 대입 가능한 임의의 안전한 패스워드 환경변수 처리 (`${DB_PASSWORD:-securepassword123}`)
- **헬스체크 (Healthcheck)**: Alembic이 구동되기 전 DB 컨테이너가 준비되었는지 감지하기 위한 `pg_isready` 스크립트 기반의 헬스체크 블록 필수 포함.

---

## [Strict Execution & Coding Constraints / 제약 조건]

1. **Volume 권한 및 설정 자동화**:
   - Ubuntu 26.04 호스트 환경에서 파일 권한 충돌이 발생하지 않도록 초기 초기화 SQL 스크립트(`/docker-entrypoint-initdb.d/`) 경로 바인딩 또는 셋업 방식을 명시할 것.

2. **하드웨어 자원 최적화 조율**:
   - 대량의 HNSW 벡터 인덱싱 성능을 확보하기 위해 PostgreSQL 설정 파라미터(`shared_buffers`, `work_mem`, `maintenance_work_mem`)를 Docker-compose의 `command` 명령 프롬프트나 설정 파일 주입 방식을 통해 튜닝 구조를 가질 것.

---

## [Self-Verification & Test Harness Protocol / 자체 검증 프로토콜]

하네스 원칙을 충족하기 위해, 생성되는 출력 코드 블록 내부에는 컨텐이너 구동 후 성공 여부를 확인하는 **검증 및 구동 쉘 스크립트(Verification Bash Script)**를 반드시 포함해야 합니다:
1. **컨테이너 빌드 및 백그라운드 구동 명령어**: `docker compose up --build -d` 실행 및 로그 추적 명령 구조 확인.
2. **Healthcheck 대기 및 연결 테스트**: `docker inspect`를 통해 서비스 `healthy` 상태를 대기한 후, `pg_isready` 검증에 성공하는 확인 루프 스크립트.
3. **pgvector 익스텐션 컴파일 유효성 검사**: 구동된 컨테이너 내부로 `exec` 진입하여 `psql`을 통해 `SHOW SHARED_PRELOAD_LIBRARIES;` 및 pgvector 관련 바이너리가 올바른 경로에 배치되었는지 확인하는 1라인 진단 커맨드 제공.

---

## [Expected Output Format / 기대하는 출력 포맷]
답변은 아래 구조에 맞추어 명확하게 출력되어야 합니다:
1. **Dockerfile**: `pgvector`를 자동으로 빌드 및 설치하는 완전한 Dockerfile 소스 코드.
2. **docker-compose.yml**: 헬스체크와 볼륨 바인딩, 리소스 파라미터 튜닝이 포함된 완전한 오케스트레이션 야믈(YAML) 코드.
3. **구동 및 검증 쉘 스크립트 (`run_and_verify.sh`)**: 의존성을 체크하고 컨테이너를 올린 뒤, 정상 컴파일 여부를 자동 진단하는 배시 스크립트 블록.