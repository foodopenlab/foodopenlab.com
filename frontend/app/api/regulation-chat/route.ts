import { NextResponse } from "next/server"
import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"
import { formatGeminiApiError, generateGeminiText } from "@/lib/server/gemini-generate"
import { formatRetrieved, lawSearch, searchQueryFromMessage } from "@/lib/server/law-api"

export const dynamic = "force-dynamic"
const BACKEND_TIMEOUT_MS = 15_000

type HistoryItem = { role: string; content: string }

async function persistRegulationExchange(
  sessionKey: string,
  userMessage: string,
  assistantMessage: string,
): Promise<string | null> {
  const origin = resolveBackendOrigin()
  if (!origin) return null
  try {
    const res = await fetch(`${origin}/chat/persist-exchange`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_key: sessionKey,
        user_message: userMessage,
        assistant_message: assistantMessage,
        query_pattern: "law",
      }),
      cache: "no-store",
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    })
    if (!res.ok) return null
    const data = (await res.json()) as { message_id?: string | null }
    return data.message_id ?? null
  } catch (e) {
    console.warn("[api/regulation-chat] persist-exchange failed:", e)
    return null
  }
}

async function fetchBackendRegulationChat(body: unknown): Promise<Response | null> {
  const origin = resolveBackendOrigin()
  if (!origin) return null
  try {
    const res = await fetch(`${origin}/regulation-chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      cache: "no-store",
      signal: AbortSignal.timeout(BACKEND_TIMEOUT_MS),
    })
    return res.ok ? res : null
  } catch (e) {
    console.warn("[api/regulation-chat] backend fetch failed, using local fallback:", e)
    return null
  }
}

export async function POST(req: Request) {
  try {
    const body = (await req.json()) as {
      message?: string
      company_type?: string
      history?: HistoryItem[]
      session_key?: string
    }
    const message = body.message?.trim() ?? ""
    const companyType = body.company_type?.trim() ?? ""
    if (!message || !companyType) {
      return NextResponse.json({ detail: "message와 company_type이 필요합니다." }, { status: 400 })
    }

    const backend = await fetchBackendRegulationChat(body)
    if (backend) {
      return new NextResponse(await backend.text(), {
        status: backend.status,
        headers: { "Content-Type": "application/json" },
      })
    }

    const sessionKey =
      (body.session_key?.trim() || `reg-${crypto.randomUUID().replace(/-/g, "").slice(0, 12)}`).slice(0, 64)

    const searchQuery = searchQueryFromMessage(message)
    const retrieved = searchQuery ? await lawSearch(searchQuery) : []
    const retrievedBlock = formatRetrieved(retrieved)

    const history = (body.history ?? []).slice(-12)
    const historyBlock = history
      .map((h) => `[${h.role === "user" ? "사용자" : "어시스턴트"}]\n${h.content}`)
      .join("\n\n")

    const systemPrompt = `당신은 식품법규 전문 AI입니다.
사용자 회사 업종: ${companyType}

아래는 관련 법령 조문입니다:
${retrievedBlock}

위 조문을 근거로 ${companyType} 업종에 적용되는 내용만 간결하게 답변하세요.
규칙:
- 핵심 위주로 글머리 기호 형태로 요약
- 법률·시행령 등 명칭은 [국가법령정보센터](https://www.law.go.kr) 링크만 사용 (세부 URL 생성 금지)
- 적용 조문은 '법령명 조문번호' 형식으로 출처 명시
- 데이터 출처: 법제처 국가법령정보센터`

    const prompt = [
      "--- 시스템 ---",
      systemPrompt,
      "--- 이전 대화 ---",
      historyBlock || "(없음)",
      `[사용자 질문]\n${message}`,
    ].join("\n\n")

    const reply = await generateGeminiText(prompt)
    const referenced_laws = retrieved
      .filter((r) => r.law_name)
      .map((r) => ({ law_name: r.law_name, article: r.article || "(조문번호 미상)" }))

    const messageId = await persistRegulationExchange(sessionKey, message, reply)

    return NextResponse.json({
      reply,
      referenced_laws,
      session_key: sessionKey,
      message_id: messageId,
    })
  } catch (e) {
    console.error("[api/regulation-chat]", e)
    const status = (e as { status?: number }).status
    if (status === 503) {
      return NextResponse.json({ detail: (e as Error).message }, { status: 503 })
    }
    const { message, status: code } = formatGeminiApiError(e)
    return NextResponse.json({ detail: message }, { status: code })
  }
}
