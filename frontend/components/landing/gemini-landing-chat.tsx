"use client"

import { useCallback, useEffect, useId, useRef, useState } from "react"
import { Bot, Loader2, User } from "lucide-react"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { GeminiLandingChatToolbar } from "@/components/landing/gemini-landing-chat-toolbar"
import { apiPath, formatApiClientError } from "@/lib/api-path"
import { GEMINI_MODEL_FAST, GEMINI_MODEL_LITE } from "@/lib/gemini-models"

type ChatMessage = { id: string; role: "user" | "assistant"; content: string }

const CHAT_API_URL = apiPath("gemini/chat")

function formatChatApiError(detail: unknown): string {
  if (typeof detail === "string") return formatApiClientError(detail)
  if (Array.isArray(detail)) {
    return formatApiClientError(
      detail
        .map((item) =>
          typeof item === "object" && item !== null && "msg" in item
            ? String((item as { msg: string }).msg)
            : JSON.stringify(item),
        )
        .join(", "),
    )
  }
  return "요청에 실패했습니다."
}

type WebSpeechCtor = new () => {
  lang: string
  interimResults: boolean
  maxAlternatives: number
  onresult: ((ev: { results: { item: (i: number) => { item: (j: number) => { transcript: string } } } }) => void) | null
  start: () => void
}

export function GeminiLandingChat({ compact = false }: { compact?: boolean }) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [model, setModel] = useState(GEMINI_MODEL_FAST)
  const [loading, setLoading] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)
  const chatInstanceId = useId()

  useEffect(() => {
    listRef.current?.scrollTo({ top: listRef.current.scrollHeight, behavior: "smooth" })
  }, [messages, loading])

  const send = useCallback(async () => {
    const text = input.trim()
    if (!text || loading) return

    const userMsg: ChatMessage = { id: crypto.randomUUID(), role: "user", content: text }
    setMessages((m) => [...m, userMsg])
    setInput("")
    setLoading(true)

    try {
      const history = [...messages, userMsg].map((m) => ({
        role: m.role,
        content: m.content,
      }))
      const res = await fetch(CHAT_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: history,
          model,
        }),
      })
      const raw = await res.text()
      let data = {} as { text?: string; error?: string; detail?: unknown }
      if (raw.trim()) {
        try {
          data = JSON.parse(raw) as { text?: string; error?: string; detail?: unknown }
        } catch {
          throw new Error(
            formatApiClientError(
              res.ok
                ? "서버 응답 형식이 올바르지 않습니다."
                : raw.slice(0, 240) || `채팅 요청 실패 (HTTP ${res.status})`,
            ),
          )
        }
      }
      if (!res.ok) {
        throw new Error(formatChatApiError(data.error ?? data.detail))
      }
      const reply = data.text?.trim() ?? ""
      if (!reply) {
        throw new Error("응답이 비어 있습니다. GEMINI_API_KEY와 Vercel 환경 변수를 확인해 주세요.")
      }
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: reply }])
    } catch (e) {
      const msg = formatApiClientError(e instanceof Error ? e.message : "오류가 발생했습니다.")
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: msg }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, messages, model])

  const startVoice = useCallback(() => {
    if (typeof window === "undefined") return
    const W = window as typeof window & {
      SpeechRecognition?: WebSpeechCtor
      webkitSpeechRecognition?: WebSpeechCtor
    }
    const SpeechRecognitionCtor = W.SpeechRecognition ?? W.webkitSpeechRecognition
    if (!SpeechRecognitionCtor) {
      window.alert("이 브라우저에서는 음성 입력을 지원하지 않습니다.")
      return
    }
    const rec = new SpeechRecognitionCtor()
    rec.lang = "ko-KR"
    rec.interimResults = false
    rec.maxAlternatives = 1
    rec.onresult = (ev) => {
      const transcript = ev.results.item(0).item(0).transcript
      if (transcript) setInput((prev) => (prev ? `${prev} ${transcript}` : transcript))
    }
    rec.start()
  }, [])

  const micDisabled = loading

  return (
    <div
      className={cn(
        "flex w-full flex-col overflow-hidden border border-border bg-card/90 shadow-lg shadow-black/20 backdrop-blur-sm",
        compact
          ? "h-full min-h-[20rem] w-full max-w-full rounded-2xl sm:min-h-[22rem]"
          : "h-full min-h-[22rem] w-full max-w-full rounded-3xl",
      )}
    >
      <div
        ref={listRef}
        className={cn(
          "flex-1 space-y-3 overflow-y-auto border-b border-border text-left",
          compact
            ? "min-h-[10rem] max-h-[min(32vh,22rem)] px-4 py-3 sm:min-h-[12rem] sm:max-h-[min(36vh,26rem)]"
            : "min-h-[11rem] max-h-[min(52vh,28rem)] px-4 py-3",
        )}
      >
        {messages.length === 0 && !loading && (
          <p className="select-none py-8 text-center text-base text-muted-foreground sm:text-lg">
            Gemini와 대화를 시작해 보세요.
          </p>
        )}
        {messages.map((m) => (
          <div key={m.id} className="flex gap-3 text-base leading-relaxed">
            <div
              className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-full sm:h-9 sm:w-9",
                m.role === "user" ? "bg-secondary text-muted-foreground" : "bg-primary text-primary-foreground",
              )}
            >
              {m.role === "user" ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
            </div>
            <p className="min-w-0 flex-1 whitespace-pre-wrap text-foreground leading-relaxed">{m.content}</p>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 pl-9 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">Gemini 응답 중…</span>
          </div>
        )}
      </div>

      <div className={cn("shrink-0", compact ? "p-4 pb-3" : "p-4 pb-3")}>
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              void send()
            }
          }}
          placeholder="무엇이든 질문하세요."
          disabled={loading}
          rows={2}
          className="min-h-0 resize-none border-0 bg-transparent px-0 py-1 text-base shadow-none focus-visible:ring-0 sm:text-lg"
          aria-label="Gemini 질문 입력"
        />

        <GeminiLandingChatToolbar
          chatInstanceId={chatInstanceId}
          model={model}
          onModelChange={setModel}
          onVoiceClick={startVoice}
          onSendClick={() => void send()}
          micDisabled={micDisabled}
          sendDisabled={loading}
          loading={loading}
        />
      </div>
    </div>
  )
}