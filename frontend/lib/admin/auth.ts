// 통합: 어드민도 유저와 같은 auth 토큰(access_token)을 쓴다. role === "admin" 으로 판정.
const ADMIN_TOKEN_KEY = "access_token"
const ADMIN_NAME_KEY = "admin_display_name"

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

/** 서명 검증은 백엔드 몫. 진입 시점에서 형식·role·만료(exp)만 걸러 stale 토큰을 차단한다. */
export function isAdminTokenValid(): boolean {
  const token = getAdminToken()
  if (!token) return false
  const payload = decodeAdminJwtPayload(token)
  if (!payload || payload.role !== "admin") return false
  if (typeof payload.exp !== "number") return false
  // exp(초) 기준 만료 여부. 요청 중 만료를 피하려 10초 여유를 둔다.
  return payload.exp * 1000 > Date.now() + 10_000
}

export function isAdminLoggedIn(): boolean {
  return isAdminTokenValid()
}

/** JWT payload (검증 없이 표시용). */
export function decodeAdminJwtPayload(
  token: string,
): { sub?: string; email?: string; role?: string; exp?: number } | null {
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
    return JSON.parse(json) as { sub?: string; email?: string; role?: string; exp?: number }
  } catch {
    return null
  }
}

export function getAdminDisplayName(): string {
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
  if (!token) {
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
  if (res.status === 401) {
    removeAdminSession()
    window.location.href = "/admin/login"
    throw new Error("인증이 만료되었습니다.")
  }
  return res
}
