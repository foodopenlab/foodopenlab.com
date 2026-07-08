import { NextResponse } from "next/server"
import { GoogleGenerativeAI } from "@google/generative-ai"
import { GEMINI_DEFAULT_MODEL, GEMINI_MODEL_FAST, isAllowedGeminiModel } from "@/lib/gemini-models"

type ClientMessage = { role: string; content: string }

function formatGeminiError(err: unknown): { message: string; status: number } {
  const raw = err instanceof Error ? err.message : String(err)
  if (raw.includes("429") || raw.toLowerCase().includes("quota")) {
    return {
      status: 429,
      message:
        `Gemini API 무료 할당량을 초과했습니다. Google AI Studio에서 사용량·결제를 확인하거나, 잠시 후 다시 시도해 주세요. (모델: ${GEMINI_MODEL_FAST})`,
    }
  }
  if (raw.includes("404") || raw.toLowerCase().includes("not found")) {
    return {
      status: 400,
      message: "요청한 Gemini 모델을 사용할 수 없습니다. 빠른 모델(2.5 Flash-Lite)로 다시 시도해 주세요.",
    }
  }
  return { status: 500, message: raw || "Gemini 요청에 실패했습니다." }
}

export async function POST(req: Request) {
  try {
    const apiKey = process.env.GEMINI_API_KEY
    if (!apiKey?.trim()) {
      return NextResponse.json(
        {
          error:
            "GEMINI_API_KEY가 서버에 없습니다. 로컬은 watcher.www/.env.local, Vercel은 프로젝트 환경 변수에 키를 설정한 뒤 재배포해 주세요.",
        },
        { status: 503 },
      )
    }

    const body = (await req.json()) as { messages?: ClientMessage[]; model?: string }
    const modelId =
      typeof body.model === "string" && isAllowedGeminiModel(body.model) ? body.model : GEMINI_DEFAULT_MODEL

    const messages = body.messages
    if (!Array.isArray(messages) || messages.length === 0) {
      return NextResponse.json({ error: "메시지가 필요합니다." }, { status: 400 })
    }

    const last = messages[messages.length - 1]
    if (last.role !== "user" || typeof last.content !== "string" || !last.content.trim()) {
      return NextResponse.json({ error: "마지막 메시지는 사용자 질문이어야 합니다." }, { status: 400 })
    }

    const genAI = new GoogleGenerativeAI(apiKey)
    const geminiModel = genAI.getGenerativeModel({
      model: modelId,
      systemInstruction:
        "당신은 RAG Watson 식품안전·HACCP 모니터링 서비스 랜딩 페이지의 Google Gemini 기반 도우미입니다. 사용자가 한국어로 물으면 한국어로, 영어로 물으면 영어로 답하세요. 간결하고 정확하게 답변하세요.",
    })

    const history = messages.slice(0, -1).map((m) => ({
      role: m.role === "user" ? ("user" as const) : ("model" as const),
      parts: [{ text: String(m.content ?? "") }],
    }))

    const chat = geminiModel.startChat({ history })
    const result = await chat.sendMessage(last.content.trim())
    const text = result.response.text()
    return NextResponse.json({ text, model: modelId })
  } catch (e) {
    console.error("[gemini/chat]", e)
    const { message, status } = formatGeminiError(e)
    return NextResponse.json({ error: message }, { status })
  }
}
