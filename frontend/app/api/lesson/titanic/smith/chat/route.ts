import { NextResponse } from "next/server"

import { getBackendOrigin } from "@/lib/backend-origin"

export const dynamic = "force-dynamic"

type ChatRole = "user" | "assistant"

function normalizeSmithChatBody(raw: Record<string, unknown>) {
  if (Array.isArray(raw.messages)) {
    return raw
  }

  const messages: Array<{ role: ChatRole; text: string }> = []
  if (Array.isArray(raw.history)) {
    for (const item of raw.history) {
      if (typeof item !== "object" || item === null) continue
      const row = item as Record<string, unknown>
      const role = row.role === "assistant" ? "assistant" : "user"
      const text =
        typeof row.text === "string"
          ? row.text
          : typeof row.content === "string"
            ? row.content
            : ""
      if (text) messages.push({ role, text })
    }
  }
  if (messages.length === 0 && typeof raw.message === "string" && raw.message.trim()) {
    messages.push({ role: "user", text: raw.message.trim() })
  }

  return {
    messages,
    systemInstruction:
      typeof raw.systemInstruction === "string" ? raw.systemInstruction : undefined,
  }
}

export async function POST(req: Request) {
  const backendUrl = `${getBackendOrigin()}/api/titanic/smith/chat`

  try {
    const raw = (await req.json()) as Record<string, unknown>
    const body = JSON.stringify(normalizeSmithChatBody(raw))
    const upstream = await fetch(backendUrl, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
      cache: "no-store",
      signal: AbortSignal.timeout(60_000),
    })
    const bodyText = await upstream.text()
    const contentType = upstream.headers.get("content-type") || "application/json"
    return new NextResponse(bodyText, {
      status: upstream.status,
      headers: { "Content-Type": contentType },
    })
  } catch {
    return NextResponse.json(
      {
        detail:
          "백엔드에 연결할 수 없습니다. com.auditor에서 uvicorn(8000)이 실행 중인지 확인하세요.",
      },
      { status: 503 },
    )
  }
}
