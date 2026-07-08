"use client"

import { useCallback, useEffect, useId, useRef, useState } from "react"
import { Anchor, Loader2, User } from "lucide-react"

import { GeminiLandingChatToolbar } from "@/components/landing/gemini-landing-chat-toolbar"
import { Textarea } from "@/components/ui/textarea"
import { cn } from "@/lib/utils"
import { formatApiClientError } from "@/lib/api-path"
import { GEMINI_MODEL_FAST } from "@/lib/gemini-models"

type ChatMessage = { id: string; role: "user" | "assistant"; content: string }

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

export function SmithCaptainChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [model, setModel] = useState(GEMINI_MODEL_FAST)
  const [loading, setLoading] = useState(false)
  const [sessionKey, setSessionKey] = useState<string | null>(null)
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
      const messagesPayload = [...messages, userMsg].map((m) => ({
        role: m.role,
        text: m.content,
      }))
      const res = await fetch("/api/lesson/titanic/smith/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ messages: messagesPayload }),
      })
      const raw = await res.text()
      let data = {} as { text?: string; session_key?: string; detail?: unknown }
      if (raw.trim()) {
        try {
          data = JSON.parse(raw) as { text?: string; session_key?: string; detail?: unknown }
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
        throw new Error(formatChatApiError(data.detail))
      }
      const reply = data.text?.trim() ?? ""
      if (!reply) {
        throw new Error("응답이 비어 있습니다. GEMINI_API_KEY 설정을 확인해 주세요.")
      }
      if (data.session_key) setSessionKey(data.session_key)
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: reply }])
    } catch (e) {
      const msg = formatApiClientError(e instanceof Error ? e.message : "오류가 발생했습니다.")
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: msg }])
    } finally {
      setLoading(false)
    }
  }, [input, loading, messages, model, sessionKey])

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

  return (
    <div
      className={cn(
        "flex w-full flex-col overflow-hidden rounded-2xl border border-border bg-background/40 shadow-lg shadow-black/10",
        "min-h-[24rem]",
      )}
    >
      <div ref={listRef} className="flex-1 space-y-3 overflow-y-auto border-b border-border px-4 py-3 text-left">
        {messages.length === 0 && !loading && (
          <p className="select-none py-8 text-center text-base text-muted-foreground sm:text-lg">
            스미스 선장에게 타이타닉에 대해 물어보세요.
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
              {m.role === "user" ? <User className="h-4 w-4" /> : <Anchor className="h-4 w-4" />}
            </div>
            <p className="min-w-0 flex-1 whitespace-pre-wrap text-foreground leading-relaxed">{m.content}</p>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 pl-9 text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span className="text-sm">스미스 선장이 답변 중…</span>
          </div>
        )}
      </div>

      <div className="shrink-0 p-4 pb-3">
        <Textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault()
              void send()
            }
          }}
          placeholder="스미스 선장에게 물어보기"
          disabled={loading}
          rows={2}
          className="min-h-0 resize-none border-0 bg-transparent px-0 py-1 text-base shadow-none focus-visible:ring-0 sm:text-lg"
          aria-label="스미스 선장 질문 입력"
        />

        <GeminiLandingChatToolbar
          chatInstanceId={chatInstanceId}
          model={model}
          onModelChange={setModel}
          onVoiceClick={startVoice}
          onSendClick={() => void send()}
          micDisabled={loading}
          sendDisabled={loading}
          loading={loading}
        />
      </div>
    </div>
  )
}
