const ADMIN_TOKEN_KEY = "admin_token"
const ADMIN_NAME_KEY = "admin_display_name"

/** FastAPI 배포 전 임시. false로 두면 로그인 필수 (NEXT_PUBLIC_ADMIN_SKIP_AUTH=false). */
export const ADMIN_AUTH_BYPASSED = process.env.NEXT_PUBLIC_ADMIN_SKIP_AUTH !== "false"

export function getAdminToken(): string | null {
  if (typeof window === "undefined") return null
  return localStorage.getItem(ADMIN_TOKEN_KEY)
}

export function setAdminToken(token: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ADMIN_TOKEN_KEY, token)
}

export function removeAdminToken(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(ADMIN_TOKEN_KEY)
}

export function setAdminDisplayName(name: string): void {
  if (typeof window === "undefined") return
  localStorage.setItem(ADMIN_NAME_KEY, name)
}

export function removeAdminDisplayName(): void {
  if (typeof window === "undefined") return
  localStorage.removeItem(ADMIN_NAME_KEY)
}

export function removeAdminSession(): void {
  removeAdminToken()
  removeAdminDisplayName()
}

export function isAdminLoggedIn(): boolean {
  if (ADMIN_AUTH_BYPASSED) return true
  return getAdminToken() !== null
}

/** JWT payload (검증 없이 표시용). */
export function decodeAdminJwtPayload(token: string): { sub?: string; email?: string; role?: string } | null {
  try {
    const part = token.split(".")[1]
    if (!part) return null
    const b64 = part.replace(/-/g, "+").replace(/_/g, "/")
    const json = decodeURIComponent(
      atob(b64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join(""),
    )
    return JSON.parse(json) as { sub?: string; email?: string; role?: string }
  } catch {
    return null
  }
}

export function getAdminDisplayName(): string {
  if (ADMIN_AUTH_BYPASSED) return "관리자 (로그인 보류)"
  if (typeof window === "undefined") return "Admin"
  const stored = localStorage.getItem(ADMIN_NAME_KEY)
  if (stored) return stored
  const t = getAdminToken()
  if (!t) return "Admin"
  const p = decodeAdminJwtPayload(t)
  return p?.email ?? "Admin"
}

export async function adminFetch(path: string, options?: RequestInit): Promise<Response> {
  if (typeof window === "undefined") {
    throw new Error("adminFetch는 클라이언트에서만 사용할 수 있습니다.")
  }
  const token = getAdminToken()
  if (!ADMIN_AUTH_BYPASSED && !token) {
    window.location.href = "/admin/login"
    throw new Error("로그인이 필요합니다.")
  }
  const headers: Record<string, string> = {}
  if (!(options?.body instanceof FormData)) headers["Content-Type"] = "application/json"
  if (token) headers.Authorization = `Bearer ${token}`
  const optHeaders = options?.headers
  if (optHeaders && typeof optHeaders === "object" && !(optHeaders instanceof Headers)) {
    Object.assign(headers, optHeaders as Record<string, string>)
  }
  const res = await fetch("/api" + path, {
    ...options,
    headers,
  })
  if (!ADMIN_AUTH_BYPASSED && res.status === 401) {
    removeAdminSession()
    window.location.href = "/admin/login"
    throw new Error("인증이 만료되었습니다.")
  }
  return res
}
