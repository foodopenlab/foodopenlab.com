"use client"

import { useState } from "react"
import { Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { adminFetch } from "@/lib/admin/auth"

type Status = "idle" | "loading" | "success" | "error"

export function BraindeadTelegramForm() {
  const [to, setTo] = useState("")
  const [prompt, setPrompt] = useState("")
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("loading")
    setMessage("")

    try {
      const res = await adminFetch("/admin/braindead/send-telegram", {
        method: "POST",
        body: JSON.stringify({ to, prompt }),
      })
      const data = (await res.json()) as { success?: boolean; message?: string; detail?: string }

      if (res.ok && data.success) {
        setStatus("success")
        setMessage(data.message ?? "발송 완료")
        setTo("")
        setPrompt("")
      } else {
        setStatus("error")
        setMessage(data.detail ?? data.message ?? "오류가 발생했습니다.")
      }
    } catch {
      setStatus("error")
      setMessage("네트워크 오류가 발생했습니다.")
    }
  }

  return (
    <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
      <CardHeader>
        <CardTitle>텔레그램 보내기</CardTitle>
        <CardDescription>
          보낼 내용을 설명하면 AI가 메시지를 작성해 텔레그램으로 발송합니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="telegram-to">Chat ID</Label>
            <Input
              id="telegram-to"
              placeholder="예: 123456789"
              value={to}
              onChange={(e) => setTo(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="telegram-prompt">보낼 내용 안내</Label>
            <Textarea
              id="telegram-prompt"
              placeholder="예: 오늘 오후 3시 미팅 참석 여부를 묻는 메시지를 보내줘"
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={5}
              required
            />
          </div>

          {message && (
            <p className={status === "success" ? "text-sm font-medium text-green-600 dark:text-green-400" : "text-sm font-medium text-destructive"}>
              {message}
            </p>
          )}

          <Button type="submit" disabled={status === "loading"} className="w-full gap-2">
            <Send className="h-4 w-4" />
            {status === "loading" ? "AI가 작성 중..." : "보내기"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
