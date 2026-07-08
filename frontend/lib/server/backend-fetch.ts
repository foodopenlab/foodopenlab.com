import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"

/** 공개 FastAPI가 설정된 경우에만 백엔드 프록시 (Vercel 사설·터널 URL 제외). */
export async function fetchBackend(path: string, init?: RequestInit): Promise<Response | null> {
  const origin = resolveBackendOrigin()
  if (!origin) return null
  const url = `${origin}${path.startsWith("/") ? path : `/${path}`}`
  try {
    return await fetch(url, {
      ...init,
      cache: "no-store",
      signal: init?.signal ?? AbortSignal.timeout(25_000),
    })
  } catch {
    return null
  }
}
