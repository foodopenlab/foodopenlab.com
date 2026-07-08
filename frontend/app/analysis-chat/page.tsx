"use client"

import { useEffect, useRef, useState } from "react"
import { Send } from "lucide-react"
import { ChatFeedbackControls } from "@/components/chat/chat-feedback-controls"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { postAnalysisChat } from "@/lib/api/analysis-chat-client"
import { renderChatMessageContent } from "@/lib/chat-message-content"
import { cn } from "@/lib/utils"

const SESSION_KEY = "analysis_chat_session"

const SUGGESTIONS: { title: string; questions: string[] }[] = [
  {
    title: "🧪 원료 성분 분석",
    questions: [
      "고춧가루의 원료 성분 및 주의사항 분석해줘",
      "L-아스코빌팔미테이트가 사용 가능한 식품유형은?",
    ],
  },
  {
    title: "⚠️ 위해 이력 조회",
    questions: [
      "최근 백후추에서 빈번하게 발생하는 위해 물질은?",
      "살모넬라균 검출로 인한 회수 조치 사례 알려줘",
    ],
  },
  {
    title: "📋 법적 규격 및 기준",
    questions: [
      "식품원료로서 사용 가능한 원료 기준이 어떻게 돼?",
      "보존료가 검출되지 않아야 하는 식품 유형 알려줘",
    ],
  },
]

type ChatMessage = {
  id?: string | null
  role: "user" | "assistant"
  content: string
}

function randomSessionKey() {
  return `web-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 10)}`
}

function getOrCreateSessionKey(): string {
  if (typeof window === "undefined") return randomSessionKey()
  let k = window.localStorage.getItem(SESSION_KEY)
  if (!k) {
    k = randomSessionKey()
    window.localStorage.setItem(SESSION_KEY, k)
  }
  return k
}

function detectToolsUsed(content: string): string[] {
  const tools = []
  const text = content.toLowerCase()
  if (text.includes("원료") || text.includes("성분") || text.includes("식품유형") || text.includes("원재료")) {
    tools.push("원료 규격/성분 식별")
  }
  if (text.includes("기준") || text.includes("규격") || text.includes("잔류") || text.includes("보존료") || text.includes("허용")) {
    tools.push("잔류 허용기준 및 규격 조회")
  }
  if (text.includes("회수") || text.includes("위해") || text.includes("살모넬라") || text.includes("검출") || text.includes("리콜") || text.includes("부적합")) {
    tools.push("식품 위해/회수 데이터베이스 조회")
  }
  if (text.includes("haccp") || text.includes("인증") || text.includes("해썹")) {
    tools.push("HACCP 인증업체 매핑")
  }
  if (tools.length === 0) {
    tools.push("공공 API 검색")
  }
  return tools
}

function detectRiskLevel(content: string): { score: number; label: "safe" | "caution" | "danger"; text: string } {
  const text = content.toLowerCase()
  let score = 30
  
  if (text.includes("회수") || text.includes("부적합") || text.includes("살모넬라") || text.includes("대장균") || text.includes("위험") || text.includes("금지")) {
    score = 85
  } else if (text.includes("주의") || text.includes("권장") || text.includes("제한") || text.includes("일부") || text.includes("위해 정보")) {
    score = 55
  } else if (text.includes("적합") || text.includes("안전") || text.includes("허용") || text.includes("인증")) {
    score = 15
  }
  
  if (score >= 75) {
    return { score, label: "danger", text: "위험 (Danger)" }
  } else if (score >= 40) {
    return { score, label: "caution", text: "주의 (Caution)" }
  } else {
    return { score, label: "safe", text: "안전 (Safe)" }
  }
}


export default function AnalysisChatPage() {
  const [sessionKey] = useState(() => getOrCreateSessionKey())
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", content: "HACCP Monitor AI입니다. 성분을 분석할 원료명이나 식품유형을 입력해 주세요." },
  ])
  const [input, setInput] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isSubmitting])

  const submit = async (text = input) => {
    const content = text.trim()
    if (!content || isSubmitting) return
    setInput("")
    setIsSubmitting(true)
    setMessages((prev) => [...prev, { role: "user", content }])

    const historyPayload = messages.slice(1).map((m) => ({ role: m.role, content: m.content }))

    try {
      const data = await postAnalysisChat({
        session_key: sessionKey,
        message: content,
        history: historyPayload,
      })
      setMessages((prev) => [...prev, { id: data.message_id, role: "assistant", content: data.reply || "(응답 없음)" }])
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: e instanceof Error ? `요청 실패: ${e.message}` : "요청에 실패했습니다.",
        },
      ])
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <main className="mx-auto grid w-full max-w-6xl flex-1 gap-4 px-4 py-6 lg:grid-cols-[16rem_1fr]">
      <aside className="flex flex-col gap-6 rounded-2xl border border-border/70 bg-card/60 p-4 lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]">
        <div>
          <h1 className="text-base font-semibold text-foreground">AI 원료 분석</h1>
          <p className="mt-1.5 text-xs text-muted-foreground">
            원료명을 입력하여 성분 규격 및 위해 이력을 편리하게 분석해 보세요.
          </p>
        </div>

        <div className="min-h-0 flex-1 space-y-5 overflow-y-auto">
          {SUGGESTIONS.map((group) => (
            <section key={group.title} className="space-y-2">
              <h2 className="text-xs font-medium text-primary">{group.title}</h2>
              {group.questions.map((question) => (
                <Button
                  key={question}
                  type="button"
                  variant="outline"
                  className="h-auto w-full justify-start whitespace-normal py-2 text-left text-xs"
                  onClick={() => void submit(question)}
                  disabled={isSubmitting}
                >
                  {question}
                </Button>
              ))}
            </section>
          ))}
        </div>
      </aside>

      <section className="flex min-h-[calc(100vh-8rem)] flex-col overflow-hidden rounded-2xl border border-border/70 bg-card/50">
        <div className="border-b border-border/70 px-5 py-4">
          <h2 className="font-semibold text-foreground">대화</h2>
          <p className="mt-1 text-sm text-muted-foreground">식품안전나라 및 AI 종합 원료 분석 서비스</p>
        </div>

        <div className="flex-1 space-y-4 overflow-y-auto p-5">
          {messages.map((message, index) => (
            <div key={`${message.role}-${index}`} className={cn("flex", message.role === "user" ? "justify-end" : "justify-start")}>
              <div
                className={cn(
                  "max-w-[78%] whitespace-pre-line rounded-2xl border-l-4 px-4 py-3 text-sm leading-relaxed",
                  message.role === "user"
                    ? "border-l-primary bg-primary text-primary-foreground"
                    : "border-l-muted-foreground/40 bg-background/80 text-foreground",
                )}
              >
                {renderChatMessageContent(message.content)}
                {message.role === "assistant" ? (
                  <div className="mt-2 space-y-3">
                    <div className="flex items-center gap-1.5">
                      <Badge variant="outline" className="text-[10px]">
                        Gemini
                      </Badge>
                    </div>

                    {index > 0 && (
                      <div className="space-y-3 border-t border-border/40 pt-3">
                        {/* Tools Used Timeline/Badges */}
                        <div>
                          <span className="text-[11px] font-semibold text-muted-foreground block mb-1">🛠️ 분석에 활성화된 도구 (Tools Used)</span>
                          <div className="flex flex-wrap gap-1">
                            {detectToolsUsed(message.content).map((tool, idx) => (
                              <Badge key={idx} variant="secondary" className="text-[10px] bg-primary/5 text-primary border border-primary/20">
                                {tool}
                              </Badge>
                            ))}
                          </div>
                        </div>

                        {/* Risk Level Gauge Bar */}
                        <div>
                          {(() => {
                            const risk = detectRiskLevel(message.content)
                            return (
                              <>
                                <div className="flex justify-between items-center text-[11px] mb-1">
                                  <span className="font-semibold text-muted-foreground">⚠️ 원료 위험도 분석 (Risk Level)</span>
                                  <span className={cn("font-bold px-1.5 py-0.5 rounded text-[10px] text-white", 
                                    risk.label === "danger" ? "bg-rose-600" : risk.label === "caution" ? "bg-amber-600" : "bg-emerald-600"
                                  )}>
                                    {risk.text}
                                  </span>
                                </div>
                                <div className="w-full h-2 rounded-full bg-muted overflow-hidden relative">
                                  <div 
                                    className={cn("h-full transition-all duration-500", 
                                      risk.label === "danger" ? "bg-rose-500" : risk.label === "caution" ? "bg-amber-500" : "bg-emerald-500"
                                    )} 
                                    style={{ width: `${risk.score}%` }} 
                                  />
                                </div>
                                <div className="flex justify-between text-[9px] text-muted-foreground mt-0.5 px-0.5">
                                  <span>안전 (0)</span>
                                  <span>주의 (50)</span>
                                  <span>위험 (100)</span>
                                </div>
                              </>
                            )
                          })()}
                        </div>
                      </div>
                    )}

                    <ChatFeedbackControls messageId={message.id} sessionKey={sessionKey} />
                  </div>
                ) : null}
              </div>
            </div>
          ))}
          {isSubmitting ? (
            <div className="flex justify-start">
              <div className="flex gap-1 rounded-2xl bg-background/80 px-4 py-3">
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.2s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.1s]" />
                <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
              </div>
            </div>
          ) : null}
          <div ref={bottomRef} />
        </div>

        <form
          className="border-t border-border/70 p-4"
          onSubmit={(e) => {
            e.preventDefault()
            void submit()
          }}
        >
          <div className="flex items-end gap-2">
            <Textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key !== "Enter" || e.shiftKey) return
                if (e.nativeEvent.isComposing) return
                e.preventDefault()
                void submit()
              }}
              placeholder="원료명, 식품유형 등을 입력하세요."
              disabled={isSubmitting}
              className="min-h-12 resize-none"
            />
            <Button type="submit" disabled={isSubmitting || !input.trim()} className="h-12 px-4">
              <Send className="h-4 w-4" />
              <span className="sr-only">전송</span>
            </Button>
          </div>
        </form>
      </section>
    </main>
  )
}
