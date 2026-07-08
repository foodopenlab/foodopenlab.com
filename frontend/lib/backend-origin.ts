/**
 * 클라이언트 컴포넌트용 백엔드 오리진.
 * Docker·로컬 모두 `/api/*` rewrite 사용을 권장합니다 (빈 문자열 = same-origin).
 */
export function getClientBackendOrigin(): string {
  const raw = (process.env.NEXT_PUBLIC_API_URL || "").trim()
  return raw ? raw.replace(/\/$/, "") : ""
}

/** 서버 Route Handler·fetch용 (Node 런타임). */
export function getBackendOrigin(): string {
  const raw = (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "").trim()
  if (raw) return raw.replace(/\/$/, "")
  return "http://127.0.0.1:8000"
}
