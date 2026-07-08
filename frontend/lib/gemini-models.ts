/** Google AI Studio 권장 모델 ID (랜딩 채팅·/api/gemini/chat 공통) */

/** 안정화 권장 — Gemini 2.5 Flash-Lite */
export const GEMINI_MODEL_FAST = "gemini-2.5-flash-lite"

/** 최신 3세대 경량 — Gemini 3.1 Flash-Lite */
export const GEMINI_MODEL_LITE = "gemini-3.1-flash-lite"

/** 2.5 Flash (Flash-Lite 대안) */
export const GEMINI_MODEL_FLASH = "gemini-2.5-flash"

export const GEMINI_ALLOWED_MODELS = [
  GEMINI_MODEL_FAST,
  GEMINI_MODEL_FLASH,
  GEMINI_MODEL_LITE,
] as const

export const GEMINI_DEFAULT_MODEL = GEMINI_MODEL_FAST

export type GeminiModelId = (typeof GEMINI_ALLOWED_MODELS)[number]

export function isAllowedGeminiModel(id: string): id is GeminiModelId {
  return (GEMINI_ALLOWED_MODELS as readonly string[]).includes(id)
}
