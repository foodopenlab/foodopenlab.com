import { formatApiClientError } from "@/lib/api-path"

export async function readApiErrorMessage(res: Response, fallback?: string): Promise<string> {
  const raw = await res.text()
  const base = fallback || res.statusText || `HTTP ${res.status}`
  if (!raw.trim()) return formatApiClientError(base)
  try {
    const data = JSON.parse(raw) as { detail?: unknown; error?: unknown }
    if (typeof data.detail === "string") return formatApiClientError(data.detail)
    if (typeof data.error === "string") return formatApiClientError(data.error)
    if (Array.isArray(data.detail)) return formatApiClientError(data.detail.map(String).join(", "))
  } catch {
    /* plain text */
  }
  return formatApiClientError(raw.slice(0, 300) || base)
}
