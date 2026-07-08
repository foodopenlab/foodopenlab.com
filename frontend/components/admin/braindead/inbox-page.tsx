"use client"

import { useCallback, useEffect, useState } from "react"
import { Inbox, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Dialog, DialogContent, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { adminFetch } from "@/lib/admin/auth"

type InboxEmail = {
  id: number
  gmail_message_id: string | null
  from_email: string
  from_name: string | null
  subject: string
  body: string
  received_at: string | null
}

function formatReceivedAt(value: string | null): string {
  if (!value) return ""
  return new Date(value).toLocaleString("ko-KR")
}

export function BraindeadInboxPage() {
  const [emails, setEmails] = useState<InboxEmail[]>([])
  const [loading, setLoading] = useState(true)
  const [selected, setSelected] = useState<InboxEmail | null>(null)

  const fetchInbox = useCallback(async () => {
    setLoading(true)
    try {
      const res = await adminFetch("/admin/braindead/inbox")
      if (res.ok) {
        setEmails((await res.json()) as InboxEmail[])
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void fetchInbox() }, [fetchInbox])

  return (
    <div className="container mx-auto max-w-5xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">BRAINDEAD · GMAIL INBOX</p>
        <h1 className="text-4xl font-black tracking-tight sm:text-5xl">수신함</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          n8n의 Gmail Trigger가 전달한 새 메일이 여기에 쌓입니다.
        </p>
      </div>

      <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <Inbox className="size-5 shrink-0 text-primary" aria-hidden />
            수신 메일 목록
          </CardTitle>
          <Button size="sm" variant="outline" className="gap-1.5" onClick={() => void fetchInbox()} disabled={loading}>
            <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
            새로고침
          </Button>
        </CardHeader>

        <CardContent>
          {loading ? (
            <p className="py-12 text-center text-sm text-muted-foreground">불러오는 중...</p>
          ) : emails.length === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">
              수신된 메일이 없습니다. n8n 워크플로우가 새 메일을 보내면 이 목록에 표시됩니다.
            </p>
          ) : (
            <ul className="divide-y divide-border/60">
              {emails.map((email) => (
                <li key={email.id}>
                  <button
                    type="button"
                    onClick={() => setSelected(email)}
                    className="flex w-full flex-col gap-1 px-1 py-3 text-left transition-colors hover:bg-muted/40"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="truncate font-semibold">{email.subject}</span>
                      <span className="shrink-0 text-xs text-muted-foreground">{formatReceivedAt(email.received_at)}</span>
                    </div>
                    <div className="flex items-center justify-between gap-3">
                      <span className="truncate text-sm text-muted-foreground">
                        {email.from_name ? `${email.from_name} <${email.from_email}>` : email.from_email}
                      </span>
                    </div>
                    <p className="line-clamp-1 text-sm text-muted-foreground/80">{email.body}</p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </CardContent>
      </Card>

      <Dialog open={selected !== null} onOpenChange={(o) => !o && setSelected(null)}>
        <DialogContent className="max-h-[85vh] max-w-2xl overflow-y-auto">
          <DialogHeader>
            <DialogTitle>{selected?.subject}</DialogTitle>
          </DialogHeader>
          {selected && (
            <div className="space-y-3">
              <p className="text-xs text-muted-foreground">
                {selected.from_name ? `${selected.from_name} <${selected.from_email}>` : selected.from_email}
                {" · "}
                {formatReceivedAt(selected.received_at)}
              </p>
              <p className="whitespace-pre-wrap break-words text-sm">{selected.body}</p>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}
