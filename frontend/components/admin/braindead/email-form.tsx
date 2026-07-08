"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { Send } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { adminFetch } from "@/lib/admin/auth"

type Status = "idle" | "loading" | "success" | "error"
type Suggestion = { id: number; name: string | null; email: string | null }

export function BraindeadEmailForm() {
  const [to, setTo] = useState("")
  const [toName, setToName] = useState("")
  const [prompt, setPrompt] = useState("")
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")
  const [suggestions, setSuggestions] = useState<Suggestion[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const wrapperRef = useRef<HTMLDivElement>(null)

  const fetchSuggestions = useCallback(async (q: string) => {
    if (!q.trim()) { setSuggestions([]); return }
    try {
      const res = await adminFetch(`/admin/braindead/contacts/search?q=${encodeURIComponent(q)}`)
      if (res.ok) setSuggestions(await res.json() as Suggestion[])
    } catch { /* silent */ }
  }, [])

  const handleToChange = (val: string) => {
    setTo(val)
    setShowSuggestions(true)
    if (debounceRef.current) clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => void fetchSuggestions(val), 250)
  }

  const selectSuggestion = (s: Suggestion) => {
    setTo(s.email ?? "")
    setToName(s.name ?? "")
    setSuggestions([])
    setShowSuggestions(false)
  }

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target as Node)) {
        setShowSuggestions(false)
      }
    }
    document.addEventListener("mousedown", handleClick)
    return () => document.removeEventListener("mousedown", handleClick)
  }, [])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("loading")
    setMessage("")

    try {
      const res = await adminFetch("/admin/braindead/send-email", {
        method: "POST",
        body: JSON.stringify({ to, prompt, to_name: toName || undefined }),
      })
      const data = (await res.json()) as { success?: boolean; message?: string; detail?: string }

      if (res.ok && data.success) {
        setStatus("success")
        setMessage(data.message ?? "발송 완료")
        setTo("")
        setToName("")
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
        <CardTitle>메일 보내기</CardTitle>
        <CardDescription>
          보낼 내용을 설명하면 AI가 이메일 본문을 작성해 발송합니다.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="email-to">받는 사람</Label>
            <div ref={wrapperRef} className="relative">
              <Input
                id="email-to"
                type="text"
                placeholder="이름 또는 이메일로 검색"
                value={to}
                onChange={(e) => handleToChange(e.target.value)}
                onFocus={() => { if (suggestions.length > 0) setShowSuggestions(true) }}
                autoComplete="off"
                required
              />
              {showSuggestions && suggestions.length > 0 && (
                <ul className="absolute z-50 mt-1 w-full rounded-md border border-border bg-card shadow-lg">
                  {suggestions.map((s) => (
                    <li
                      key={s.id}
                      onMouseDown={() => selectSuggestion(s)}
                      className="flex cursor-pointer flex-col px-3 py-2 hover:bg-muted"
                    >
                      <span className="text-sm font-medium">{s.name ?? "-"}</span>
                      <span className="text-xs text-muted-foreground">{s.email ?? "-"}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="email-prompt">보낼 내용 안내</Label>
            <Textarea
              id="email-prompt"
              placeholder="예: 내일 오후 2시 회의 일정을 알리는 이메일을 보내줘"
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
