export type AnalysisChatRequest = {
  session_key: string
  message: string
  history: { role: string; content: string }[]
}

import { formatApiClientError } from "@/lib/api-path"

export type AnalysisChatResponse = {
  reply: string
  session_key: string
  message_id?: string | null
}

function extractDetail(data: unknown, fallback: string): string {
  if (data && typeof data === "object" && "detail" in data) {
    const d = (data as { detail?: unknown }).detail
    if (typeof d === "string") return d
    if (Array.isArray(d)) return d.map(String).join(", ")
  }
  return fallback
}

export async function postAnalysisChat(body: AnalysisChatRequest): Promise<AnalysisChatResponse> {
  const res = await fetch("/api/analysis-chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
    cache: "no-store",
  })

  const raw = await res.text()
  let data: unknown = null
  if (raw.trim()) {
    try {
      data = JSON.parse(raw) as unknown
    } catch {
      throw new Error(raw.slice(0, 300) || res.statusText || "응답을 해석할 수 없습니다.")
    }
  }

  if (!res.ok) {
    const detail = extractDetail(data, raw.slice(0, 300) || res.statusText || `HTTP ${res.status}`)
    throw new Error(formatApiClientError(detail))
  }

  const parsed = data as AnalysisChatResponse | null
  if (!parsed || typeof parsed.reply !== "string") {
    throw new Error("서버 응답 형식이 올바르지 않습니다.")
  }

  return {
    reply: parsed.reply,
    session_key: typeof parsed.session_key === "string" ? parsed.session_key : body.session_key,
    message_id: typeof parsed.message_id === "string" ? parsed.message_id : null,
  }
}
