# 1. Node.js 베이스 이미지 선택 (로컬: v24.15.0)
FROM node:24-alpine

# 2. 컨테이너 내 작업 디렉토리 설정
WORKDIR /app

# 3. 의존성 파일 복사 및 설치
COPY package.json package-lock.json* ./
RUN npm install

# 4. 나머지 소스 코드 복사
COPY . .

# 5. Next.js 개발 서버 실행 (3000 포트)
EXPOSE 3000
CMD ["npm", "run", "dev"]
