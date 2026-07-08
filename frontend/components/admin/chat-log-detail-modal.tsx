"use client"

import { useEffect, useState } from "react"
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Spinner } from "@/components/ui/spinner"
import { adminFetch } from "@/lib/admin/auth"
import { cn } from "@/lib/utils"

type Message = {
  id: string
  role: string
  content: string
  created_at: string
}

type Detail = {
  session: {
    session_id: string
    chat_type: string
    company_type: string | null
    message_count: number
    created_at: string
    updated_at: string
  }
  messages: Message[]
}

type Props = {
  sessionId: string | null
  chatType?: string | null
  open: boolean
  onClose: () => void
}

export function ChatLogDetailModal({ sessionId, chatType, open, onClose }: Props) {
  const [data, setData] = useState<Detail | null>(null)
  const [loading, setLoading] = useState(false)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    if (!open || !sessionId) {
      setData(null)
      setErr(null)
      return
    }
    const run = async () => {
      setLoading(true)
      setErr(null)
      try {
        const enc = encodeURIComponent(sessionId)
        const qs = chatType ? `?chat_type=${encodeURIComponent(chatType)}` : ""
        const res = await adminFetch(`/admin/chat-logs/${enc}${qs}`)
        if (!res.ok) throw new Error("fail")
        setData((await res.json()) as Detail)
      } catch {
        setErr("상세를 불러올 수 없습니다.")
        setData(null)
      } finally {
        setLoading(false)
      }
    }
    void run()
  }, [open, sessionId, chatType])

  const s = data?.session

  return (
    <Dialog open={open} onOpenChange={(o) => !o && onClose()}>
      <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex flex-wrap items-center gap-2">
            {s ? (
              <>
                {s.chat_type === "analysis" || s.chat_type === "ingredient" ? (
                  <Badge className="bg-blue-500/20 text-blue-300">원료 분석</Badge>
                ) : (
                  <Badge className="bg-emerald-500/20 text-emerald-300">법규 채팅</Badge>
                )}
                <span className="font-mono text-sm font-normal text-muted-foreground">{s.session_id}</span>
              </>
            ) : (
              "채팅 상세"
            )}
          </DialogTitle>
        </DialogHeader>
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner className="size-8" />
          </div>
        ) : err ? (
          <p className="text-center text-sm text-destructive">{err}</p>
        ) : s ? (
          <div className="space-y-4">
            {s.chat_type === "regulation" && s.company_type ? (
              <p className="text-sm text-muted-foreground">업종: {s.company_type}</p>
            ) : null}
            <p className="text-xs text-muted-foreground">
              생성: {new Date(s.created_at).toLocaleString("ko-KR")}
            </p>
            <div className="flex flex-col gap-3 border-t border-border pt-4">
              {(data?.messages ?? []).map((m) => (
                <div
                  key={m.id}
                  className={cn("flex w-full", m.role === "user" ? "justify-end" : "justify-start")}
                >
                  <div
                    className={cn(
                      "max-w-[85%] rounded-lg px-3 py-2 text-sm",
                      m.role === "user"
                        ? "bg-primary text-primary-foreground"
                        : "border border-border bg-card text-card-foreground",
                    )}
                  >
                    <p className="whitespace-pre-wrap break-words">{m.content}</p>
                    <p className="mt-1 text-[10px] opacity-80">
                      {new Date(m.created_at).toLocaleTimeString("ko-KR")}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ) : null}
        <div className="flex justify-end pt-2">
          <Button type="button" variant="secondary" onClick={onClose}>
            닫기
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
