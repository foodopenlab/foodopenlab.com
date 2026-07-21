# syntax=docker/dockerfile:1

# 1. Python 베이스 이미지 선택 (로컬 .venv: Python 3.13.9)
FROM python:3.13-slim

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3-1. 무거운 의존성(torch/langchain/neo4j 등) 먼저 설치.
#      requirements.txt만 바뀌고 이 파일이 그대로면 이 레이어는 캐시로 재사용됨 — 재다운로드 없음.
COPY requirements-heavy.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements-heavy.txt

# 3-1b. OpenCV(cv2) 런타임 시스템 라이브러리 — slim 이미지엔 없어서 import 실패함.
#       heavy 레이어 '뒤'에 두어 torch 캐시(7GB)를 보존한다. 앞에 두면 heavy가 무효화됨.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 3-2. 나머지(자주 바뀌는) 의존성. heavy 패키지는 이미 설치돼 있어 스킵되고 델타만 설치됨.
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip pip install -r requirements.txt

# 4. 나머지 소스 코드 복사
COPY . .

# 5. FastAPI 실행 (com.auditor/main.py)
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
