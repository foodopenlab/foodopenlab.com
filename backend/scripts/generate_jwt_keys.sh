#!/usr/bin/env bash
#
# RS256 키페어 생성 — apps/auth 인증 게이트웨이용.
#   개인키(jwt_private.pem) → .env.auth 의 JWT_PRIVATE_KEY  (발급 컨테이너 전용)
#   공개키(jwt_public.pem)  → .env.backend 의 JWT_PUBLIC_KEY (모든 검증 컨테이너)
#
# 멀티라인 PEM은 base64로 인코딩해 env 단일 라인으로 주입한다(config에서 디코드).
# PEM 파일은 .gitignore(`*.pem`)로 커밋되지 않는다.
#
set -euo pipefail

OUT_DIR="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/keys}"
PRIV="${OUT_DIR}/jwt_private.pem"
PUB="${OUT_DIR}/jwt_public.pem"

mkdir -p "${OUT_DIR}"

if [[ -f "${PRIV}" || -f "${PUB}" ]]; then
  echo "❌ 이미 키가 존재합니다: ${OUT_DIR}" >&2
  echo "   덮어쓰려면 기존 PEM을 먼저 삭제하세요 (기존 토큰이 전부 무효화됩니다)." >&2
  exit 1
fi

openssl genrsa -out "${PRIV}" 2048
openssl rsa -in "${PRIV}" -pubout -out "${PUB}"
chmod 600 "${PRIV}"

echo ""
echo "✅ 생성 완료: ${OUT_DIR}"
echo ""
echo "── .env.auth (발급 컨테이너 전용) ──────────────────────────────"
echo "JWT_PRIVATE_KEY_B64=$(base64 -w0 "${PRIV}")"
echo ""
echo "── .env.backend (검증 컨테이너 공용) ───────────────────────────"
echo "JWT_PUBLIC_KEY_B64=$(base64 -w0 "${PUB}")"
echo ""
echo "주의: JWT_PRIVATE_KEY_B64 는 .env.auth 에만 넣습니다. 검증 컨테이너에 절대 넣지 마세요."
