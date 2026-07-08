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

export function BraindeadDiscordForm() {
  const [channel, setChannel] = useState("")
  const [prompt, setPrompt] = useState("")
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("loading")
    setMessage("")

    try {
      const res = await adminFetch("/admin/braindead/send-discord", {
        method: "POST",
        body: JSON.stringify({ channel, prompt }),
      })
      const data = (await res.json()) as { success?: boolean; message?: string; detail?: string }

      if (res.ok && data.success) {
        setStatus("success")
        setMessage(data.message ?? "발송 완료")
        setChannel("")
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
        <CardTitle>디스코드 보내기</CardTitle>
        <CardDescription>
          보낼 내용을 설명하면 AI가 메시지를 작성해 디스코드로 발송합니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="discord-channel">채널 (Webhook URL 또는 Channel ID)</Label>
            <Input
              id="discord-channel"
              placeholder="예: https://discord.com/api/webhooks/..."
              value={channel}
              onChange={(e) => setChannel(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="discord-prompt">보낼 내용 안내</Label>
            <Textarea
              id="discord-prompt"
              placeholder="예: 신규 업데이트 배포 완료 공지를 보내줘"
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
