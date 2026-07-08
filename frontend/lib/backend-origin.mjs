/**
 * next.config.mjs 전용 — rewrite 대상 백엔드 오리진.
 * 프로덕션에서는 공개 URL만 허용 (Vercel DNS_HOSTNAME_RESOLVED_PRIVATE 방지).
 */

const PRIVATE_HOSTS = new Set([
  "localhost",
  "127.0.0.1",
  "0.0.0.0",
  "::1",
])

function isPrivateHostname(hostname) {
  const h = hostname.toLowerCase()
  if (PRIVATE_HOSTS.has(h)) return true
  if (h.endsWith(".local")) return true
  if (/^10\./.test(h)) return true
  if (/^192\.168\./.test(h)) return true
  if (/^172\.(1[6-9]|2\d|3[0-1])\./.test(h)) return true
  return false
}

const TUNNEL_HOST_PATTERNS = [
  /\.ngrok/i,
  /\.ngrok-free\.app$/i,
  /\.loca\.lt$/i,
  /\.localhost\.run$/i,
  /\.trycloudflare\.com$/i,
]

/** 프론트 도메인을 BACKEND_URL로 쓰면 rewrite가 자기 자신을 호출함 */
const FRONTEND_HOSTS = new Set([
  "foodopenlab.com",
  "www.foodopenlab.com",
])

export function isPrivateOrigin(url) {
  try {
    const { hostname } = new URL(url)
    const h = hostname.toLowerCase()
    if (isPrivateHostname(h)) return true
    if (FRONTEND_HOSTS.has(h)) return true
    return TUNNEL_HOST_PATTERNS.some((re) => re.test(h))
  } catch {
    return true
  }
}

/**
 * @returns {string | null} rewrite에 쓸 백엔드 오리진 (슬래시 없음), 없으면 null
 */
export function resolveBackendOrigin() {
  const raw = (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "").trim()
  const isProd = process.env.VERCEL === "1"

  if (raw) {
    const origin = raw.replace(/\/$/, "")
    if (isProd && isPrivateOrigin(origin)) {
      console.warn(
        "[next.config] BACKEND_URL이 사설·터널·프론트 도메인입니다. " +
          "해당 경로는 Next.js API 라우트가 처리합니다. 공개 FastAPI URL만 rewrite에 사용하세요.",
      )
      return null
    }
    return origin
  }

  if (!isProd) {
    return "http://127.0.0.1:8000"
  }

  console.warn("[next.config] BACKEND_URL 미설정 — /api/* rewrite가 비활성화됩니다.")
  return null
}

/** Route Handler·서버 fetch용 백엔드 오리진 (슬래시 없음). */
export function getBackendOrigin() {
  const raw = (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "").trim()
  if (raw) return raw.replace(/\/$/, "")
  return "http://127.0.0.1:8000"
}
