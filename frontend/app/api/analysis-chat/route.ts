import { NextResponse } from "next/server"
import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"
import { ANALYSIS_CHAT_SYSTEM_PROMPT } from "@/lib/chat-message-content"
import { formatGeminiApiError, generateGeminiText } from "@/lib/server/gemini-generate"

export const dynamic = "force-dynamic"
const BACKEND_TIMEOUT_MS = 15_000

type HistoryItem = { role: string; content: string }

async function fetchBackendAnalysisChat(body: unknown): Promise<Response | null> {
  const origin = resolveBackendOrigin()
  if (!origin) return null
  try {
    const res = await fetch(`${origin}/analysis-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    })
    return res.ok ? res : null
  } catch (e) {
    console.warn("[api/analysis-chat] backend fetch failed, using local fallback:", e)
    return null
  }
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as {
      session_key?: string
      message?: string
      history?: HistoryItem[]
    }
    const message = body.message?.trim() ?? ""
    const sessionKey = (body.session_key?.trim() || `web-${Date.now().toString(36)}`).slice(0, 64)
    if (!message) {
      return NextResponse.json({ detail: "message가 필요합니다." }, { status: 400 })
    }

    const backend = await fetchBackendAnalysisChat(body)
    if (backend) {
      return new NextResponse(await backend.text(), {
        status: backend.status,
        headers: { "Content-Type": "application/json" },
      })
    }

    const history = (body.history ?? []).slice(-10)
    const hist = history
      .map((h) => {
        const role = h.role === "assistant" ? "어시스턴트" : "사용자"
        return `${role}: ${h.content}`
      })
      .join("\n")

    const prompt = [ANALYSIS_CHAT_SYSTEM_PROMPT, hist ? `이전 대화:\n${hist}` : "", `사용자: ${message}`]
      .filter(Boolean)
      .join("\n\n")

    const reply = await generateGeminiText(prompt)
    return NextResponse.json({ reply, session_key: sessionKey })
  } catch (e) {
    console.error("[api/analysis-chat]", e)
    const status = (e as { status?: number }).status
    if (status === 503) {
      return NextResponse.json({ detail: (e as Error).message }, { status: 503 })
    }
    const { message, status: code } = formatGeminiApiError(e)
    return NextResponse.json({ detail: message }, { status: code })
  }
}
