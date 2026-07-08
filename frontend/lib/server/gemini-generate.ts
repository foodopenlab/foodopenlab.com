import { GoogleGenerativeAI } from "@google/generative-ai"
import { GEMINI_DEFAULT_MODEL, isAllowedGeminiModel } from "@/lib/gemini-models"

export function formatGeminiApiError(err: unknown): { message: string; status: number } {
  const raw = err instanceof Error ? err.message : String(err)
  if (raw.includes("429") || raw.toLowerCase().includes("quota")) {
    return {
      status: 429,
      message:
        "Gemini API 무료 할당량을 초과했습니다. Google AI Studio에서 사용량·결제를 확인하거나, 잠시 후 다시 시도해 주세요.",
    }
  }
  if (raw.includes("404") || raw.toLowerCase().includes("not found")) {
    return {
      status: 400,
      message: "요청한 Gemini 모델을 사용할 수 없습니다. 다른 모델을 선택해 주세요.",
    }
  }
  return { status: 500, message: raw || "Gemini 요청에 실패했습니다." }
}

export async function generateGeminiText(
  prompt: string,
  modelId = GEMINI_DEFAULT_MODEL,
): Promise<string> {
  const apiKey = process.env.GEMINI_API_KEY?.trim()
  if (!apiKey) {
    throw Object.assign(new Error("GEMINI_API_KEY가 설정되지 않았습니다."), { status: 503 })
  }
  const model = isAllowedGeminiModel(modelId) ? modelId : GEMINI_DEFAULT_MODEL
  const genAI = new GoogleGenerativeAI(apiKey)
  const geminiModel = genAI.getGenerativeModel({ model })
  const result = await geminiModel.generateContent(prompt)
  const text = result.response.text()?.trim() ?? ""
  if (!text) throw new Error("모델이 비어 있는 응답을 반환했습니다.")
  return text
}
