"use client"

import { useEffect, useRef, useState } from "react"
import { Send } from "lucide-react"
import { ChatFeedbackControls } from "@/components/chat/chat-feedback-controls"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { CompanyTypeSelector } from "@/components/regulation/company-type-selector"
import { LawReferenceBadge, type ReferencedLaw } from "@/components/regulation/law-reference-badge"
import { formatApiClientError } from "@/lib/api-path"
import { readApiErrorMessage } from "@/lib/api-parse-error"
import { renderChatMessageContent } from "@/lib/chat-message-content"
import { cn } from "@/lib/utils"

type ChatMessage = {
  id?: string | null
  role: "user" | "assistant"
  content: string
  referenced_laws?: ReferencedLaw[]
}

const WELCOME_ASSISTANT: ChatMessage = {
  role: "assistant",
  content: "식품법규 AI입니다. 업종을 선택하면 해당 업종에 적용되는 법규를 맞춤으로 안내해드립니다.",
}

const SESSION_KEY_STORAGE = "regulation_chat_session"

function getRegulationSessionKey(): string {
  if (typeof window === "undefined") return "reg-ssr"
  let key = localStorage.getItem(SESSION_KEY_STORAGE)
  if (!key) {
    key = `reg-${crypto.randomUUID().replace(/-/g, "").slice(0, 16)}`
    localStorage.setItem(SESSION_KEY_STORAGE, key)
  }
  return key
}

const SUGGESTIONS: { title: string; questions: string[] }[] = [
  {
    title: "📋 개정 법규 확인",
    questions: ["최근 식품위생법 개정사항 알려줘", "표시기준 변경된 내용 있어?", "HACCP 의무 대상 업종 기준이 바뀌었나?"],
  },
  {
    title: "⚖️ 업종별 의무사항",
    questions: ["우리 업종에서 지켜야 할 표시사항은?", "자가품질검사 주기가 어떻게 돼?", "원산지 표시 의무 대상인가?"],
  },
  {
    title: "🔍 위반·처분 기준",
    questions: ["이 위반사항 처분 기준이 뭐야?", "과징금 부과 기준 알려줘"],
  },
]

export default function RegulationChatPage() {
  const [companyType, setCompanyType] = useState("")
  const [pendingCompanyType, setPendingCompanyType] = useState<string | null>(null)
  const [changeDialogOpen, setChangeDialogOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_ASSISTANT])
  const [history, setHistory] = useState<{ role: string; content: string }[]>([])
  const [input, setInput] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [sessionKey, setSessionKey] = useState("")
  const bottomRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    setSessionKey(getRegulationSessionKey())
  }, [])

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, isSubmitting])

  const resetConversation = () => {
    setMessages([WELCOME_ASSISTANT])
    setHistory([])
    setInput("")
  }

  const applyCompanyType = (next: string) => {
    setCompanyType(next)
    resetConversation()
  }

  const onCompanySelect = (next: string) => {
    if (next === companyType) return
    if (companyType && messages.length > 1) {
      setPendingCompanyType(next)
      setChangeDialogOpen(true)
      return
    }
    applyCompanyType(next)
  }

  const confirmCompanyChange = () => {
    if (pendingCompanyType) {
      applyCompanyType(pendingCompanyType)
    }
    setPendingCompanyType(null)
    setChangeDialogOpen(false)
  }

  const cancelCompanyChange = () => {
    setPendingCompanyType(null)
    setChangeDialogOpen(false)
  }

  const submit = async (text = input) => {
    const content = text.trim()
    if (!content || isSubmitting || !companyType) return

    setInput("")
    setIsSubmitting(true)

    const userMsg: ChatMessage = { role: "user", content }
    setMessages((prev) => [...prev, userMsg])

    const nextHistory = [...history, { role: "user", content: userMsg.content }]

    try {
      const res = await fetch("/api/regulation-chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: content,
          company_type: companyType,
          history,
          session_key: sessionKey || undefined,
        }),
      })
      if (!res.ok) {
        throw new Error(await readApiErrorMessage(res))
      }
      const data = (await res.json()) as {
        reply: string
        referenced_laws: ReferencedLaw[]
        session_key?: string
        message_id?: string | null
      }
      if (data.session_key && data.session_key !== sessionKey) {
        setSessionKey(data.session_key)
        if (typeof window !== "undefined") {
          localStorage.setItem(SESSION_KEY_STORAGE, data.session_key)
        }
      }
      const assistantMsg: ChatMessage = {
        id: data.message_id,
        role: "assistant",
        content: data.reply,
        referenced_laws: data.referenced_laws ?? [],
      }
      setMessages((prev) => [...prev, assistantMsg])
      setHistory([
        ...nextHistory,
        { role: "assistant", content: assistantMsg.content },
      ])
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            e instanceof Error
              ? formatApiClientError(
                  e.message.startsWith("요청 처리")
                    ? e.message
                    : `요청 처리 중 오류가 발생했습니다: ${e.message}`,
                )
              : "요청 처리 중 오류가 발생했습니다.",
        },
      ])
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <>
      <AlertDialog open={changeDialogOpen} onOpenChange={setChangeDialogOpen}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>업종 변경</AlertDialogTitle>
            <AlertDialogDescription>
              업종을 변경하면 대화 내용이 초기화됩니다. 계속하시겠습니까?
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel type="button" onClick={cancelCompanyChange}>
              취소
            </AlertDialogCancel>
            <AlertDialogAction type="button" onClick={confirmCompanyChange}>
              변경
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <main className="mx-auto grid w-full max-w-7xl flex-1 gap-4 px-4 py-6 lg:grid-cols-[16rem_1fr_18rem]">
        <aside className="flex flex-col gap-6 rounded-2xl border border-border/70 bg-card/60 p-4 lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]">
          <div>
            <h1 className="text-base font-semibold text-foreground">법규 채팅</h1>
            <p className="mt-1 text-xs text-muted-foreground">업종을 선택한 뒤 질문해 주세요.</p>
          </div>

          <CompanyTypeSelector value={companyType} onValueChange={onCompanySelect} disabled={isSubmitting} />

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
                    disabled={isSubmitting || !companyType}
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
            {!companyType ? (
              <p className="mt-1 text-sm text-amber-600 dark:text-amber-400">왼쪽에서 업종을 먼저 선택해주세요.</p>
            ) : (
              <p className="mt-1 text-sm text-muted-foreground">선택 업종: {companyType}</p>
            )}
          </div>

          <div className="flex-1 space-y-4 overflow-y-auto p-5">
            {messages.map((message, index) => (
              <ChatBubble key={`${message.role}-${index}`} message={message} sessionKey={sessionKey} />
            ))}
            {isSubmitting ? <TypingIndicator /> : null}
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
                placeholder={companyType ? "법규 관련 질문을 입력하세요." : "업종 선택 후 입력할 수 있습니다."}
                disabled={isSubmitting || !companyType}
                className="min-h-12 resize-none"
              />
              <Button type="submit" disabled={isSubmitting || !companyType || !input.trim()} className="h-12 px-4">
                <Send className="h-4 w-4" />
                <span className="sr-only">전송</span>
              </Button>
            </div>
          </form>
        </section>

        {/* Referenced Laws Index Card Panel (Right Sidebar) */}
        <aside className="hidden flex-col gap-4 rounded-2xl border border-border/70 bg-card/60 p-4 lg:flex lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]">
          <div>
            <h2 className="text-sm font-semibold tracking-wider uppercase text-muted-foreground">⚖️ 참조 법령 인덱스</h2>
            <p className="mt-1 text-[11px] text-muted-foreground">대화 중 인용된 법정 조문 목록입니다.</p>
          </div>

          <div className="flex-1 overflow-y-auto space-y-2 pr-1">
            {(() => {
              const allReferencedLaws = messages
                .flatMap((msg) => msg.referenced_laws || [])
                .filter((law, index, self) => 
                  self.findIndex((l) => l.law_name === law.law_name && l.article === law.article) === index
                )

              if (allReferencedLaws.length === 0) {
                return (
                  <div className="flex h-full flex-col items-center justify-center text-center text-muted-foreground p-4">
                    <span className="text-xl mb-1.5">⚖️</span>
                    <p className="text-xs font-medium">참조 법령 없음</p>
                    <p className="text-[10px] text-muted-foreground/60 mt-1">대화가 시작되면 자동으로 빌드됩니다.</p>
                  </div>
                )
              }

              return allReferencedLaws.map((law, idx) => {
                const cleanArticle = (law.article || "").trim()
                const hasArticle = cleanArticle && cleanArticle !== "(조문번호 미상)"
                const url = hasArticle
                  ? `https://www.law.go.kr/법령/${encodeURIComponent(law.law_name)}/${encodeURIComponent(cleanArticle)}`
                  : `https://www.law.go.kr/법령/${encodeURIComponent(law.law_name)}`
                
                return (
                  <a
                    key={`${law.law_name}-${law.article}-${idx}`}
                    href={url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="block rounded-xl border border-border/50 bg-background/50 p-2.5 shadow-sm hover:border-primary/50 hover:bg-primary/5 transition-all duration-200 group"
                  >
                    <div className="flex justify-between items-start gap-1">
                      <span className="font-semibold text-xs text-foreground group-hover:text-primary transition-colors leading-normal line-clamp-2">
                        {law.law_name}
                      </span>
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                        strokeWidth={1.8}
                        stroke="currentColor"
                        className="h-3 w-3 text-muted-foreground group-hover:text-primary shrink-0 transition-colors opacity-60 mt-0.5"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
                        />
                      </svg>
                    </div>
                    <div className="text-[10px] text-primary/80 font-medium mt-1">
                      {law.article || "(조문번호 미상)"}
                    </div>
                  </a>
                )
              })
            })()}
          </div>
        </aside>
      </main>
    </>
  )
}

function ChatBubble({ message, sessionKey }: { message: ChatMessage; sessionKey: string }) {
  const isUser = message.role === "user"
  return (
    <div className={cn("flex", isUser ? "justify-end" : "justify-start")}>
      <div
        className={cn(
          "max-w-[78%] whitespace-pre-line rounded-2xl border-l-4 px-4 py-3 text-sm leading-relaxed",
          isUser ? "border-l-primary bg-primary text-primary-foreground" : "border-l-muted-foreground/40 bg-muted/90 text-foreground",
        )}
      >
        {renderChatMessageContent(message.content)}
        {!isUser && message.referenced_laws?.length ? (
          <LawReferenceBadge laws={message.referenced_laws} className="mt-3 border-t border-border/50 pt-3 lg:hidden" />
        ) : null}
        {!isUser ? <ChatFeedbackControls messageId={message.id} sessionKey={sessionKey} /> : null}
      </div>
    </div>
  )
}

function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="flex gap-1 rounded-2xl bg-muted/90 px-4 py-3">
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.2s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground [animation-delay:-0.1s]" />
        <span className="h-2 w-2 animate-bounce rounded-full bg-muted-foreground" />
      </div>
    </div>
  )
}
