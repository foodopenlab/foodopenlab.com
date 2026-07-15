import { NextResponse } from "next/server"
import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"

// 시맨틱 게이트웨이 단일 진입점으로 프록시.
// (기존 백엔드 /analysis-chat 직접 호출 및 프론트 Gemini fallback 제거 —
//  질문 유형 분기·감사로그·rate limit은 백엔드 게이트웨이에서 처리)

export const dynamic = "force-dynamic"
const GATEWAY_TIMEOUT_MS = 90_000

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as { session_key?: string; message?: string }
    const message = body.message?.trim() ?? ""
    if (!message) {
      return NextResponse.json({ detail: "message가 필요합니다." }, { status: 400 })
    }

    const origin = resolveBackendOrigin()
    if (!origin) {
      return NextResponse.json({ detail: "백엔드 서버에 연결할 수 없습니다." }, { status: 503 })
    }

    const sessionKey = (body.session_key?.trim() || `web-${Date.now().toString(36)}`).slice(0, 64)

    const res = await fetch(`${origin}/api/gateway/ask`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: message }),
      cache: "no-store",
      signal: AbortSignal.timeout(GATEWAY_TIMEOUT_MS),
    })

    if (!res.ok) {
      const detail = await res.text()
      return NextResponse.json({ detail: detail || "게이트웨이 요청에 실패했습니다." }, { status: res.status })
    }

    const data = (await res.json()) as { answer: string; destination: string; blocked: boolean }
    return NextResponse.json({ reply: data.answer, session_key: sessionKey, destination: data.destination })
  } catch (e) {
    console.error("[api/analysis-chat→gateway]", e)
    return NextResponse.json({ detail: "요청에 실패했습니다." }, { status: 500 })
  }
}
