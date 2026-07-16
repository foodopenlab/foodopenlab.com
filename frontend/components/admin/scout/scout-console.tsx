"use client"

import { useState } from "react"
import { FileSearch, Play, Radar } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Textarea } from "@/components/ui/textarea"
import { adminFetch } from "@/lib/admin/auth"

type Mode = "crawler" | "scraper"
type Status = "idle" | "loading" | "success" | "error"

type ScoutResponse = {
  mode: Mode
  plan: {
    max_pages: number
    max_depth: number
    max_items: number
    keywords: string[]
    reason: string
  }
  summary: Record<string, unknown>
  detail?: string
}

const MODE_META: Record<Mode, { title: string; desc: string; placeholder: string }> = {
  crawler: {
    title: "크롤러",
    desc: "시드 URL에서 같은 도메인 링크를 따라가며 페이지를 수집합니다.",
    placeholder: "예: 식품 안전 관련 페이지를 깊이 2로 30페이지까지 수집해줘",
  },
  scraper: {
    title: "스크래퍼",
    desc: "입력한 URL의 본문을 스크랩해 정제 전 결과로 저장합니다.",
    placeholder: "예: 이 페이지 본문을 스크랩하고 리콜 키워드만 저장해줘",
  },
}

const SUMMARY_LABELS: Record<string, string> = {
  seed: "시드",
  keywords: "키워드",
  pages_visited: "방문 페이지",
  findings_saved: "저장된 관련 URL",
  urls_enqueued: "적재 URL",
  urls_processed: "처리 URL",
  items_scraped: "스크랩 항목",
}

export function ScoutConsole() {
  const [mode, setMode] = useState<Mode>("crawler")
  const [url, setUrl] = useState("")
  const [command, setCommand] = useState("")
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")
  const [result, setResult] = useState<ScoutResponse | null>(null)

  const meta = MODE_META[mode]

  function switchMode(next: string) {
    setMode(next as Mode)
    setStatus("idle")
    setMessage("")
    setResult(null)
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setStatus("loading")
    setMessage("")
    setResult(null)

    try {
      const res = await adminFetch("/admin/scout", {
        method: "POST",
        body: JSON.stringify({ mode, url: url.trim(), command: command.trim() }),
      })
      const data = (await res.json().catch(() => ({}))) as ScoutResponse

      if (res.ok && data.plan) {
        setStatus("success")
        setResult(data)
      } else {
        setStatus("error")
        setMessage(data.detail ?? "실행에 실패했습니다.")
      }
    } catch {
      setStatus("error")
      setMessage("네트워크 오류가 발생했습니다.")
    }
  }

  return (
    <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
      <CardHeader>
        <CardTitle>데이터 수집 콘솔</CardTitle>
        <CardDescription>
          탭으로 크롤러/스크래퍼를 전환하고, 주소와 자연어 명령을 입력해 실행하세요.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <Tabs value={mode} onValueChange={switchMode}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="crawler" className="gap-2">
              <Radar className="h-4 w-4" />
              크롤러
            </TabsTrigger>
            <TabsTrigger value="scraper" className="gap-2">
              <FileSearch className="h-4 w-4" />
              스크래퍼
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <p className="text-sm text-muted-foreground">{meta.desc}</p>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-1.5">
            <Label htmlFor="scout-url">사이트 주소</Label>
            <Input
              id="scout-url"
              type="url"
              inputMode="url"
              placeholder="https://example.com"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              required
            />
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="scout-command">자연어 명령</Label>
            <Textarea
              id="scout-command"
              placeholder={meta.placeholder}
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              rows={4}
            />
            <p className="text-xs text-muted-foreground">
              비워 두면 기본값(페이지 20·깊이 2·항목 50)으로 실행합니다.
            </p>
          </div>

          {status === "error" && message && (
            <p className="text-sm font-medium text-destructive">{message}</p>
          )}

          <Button type="submit" disabled={status === "loading"} className="w-full gap-2">
            <Play className="h-4 w-4" />
            {status === "loading" ? `${meta.title} 실행 중…` : `${meta.title} 실행`}
          </Button>
        </form>

        {result && <ScoutResultView result={result} />}
      </CardContent>
    </Card>
  )
}

function ScoutResultView({ result }: { result: ScoutResponse }) {
  const { plan, summary } = result

  return (
    <div className="space-y-4 rounded-lg border border-border/60 bg-muted/20 p-4">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">AI 해석</p>
        <p className="mt-1 text-sm text-foreground">
          {plan.reason || "명령 없이 기본값으로 실행했습니다."}
        </p>
      </div>

      <div className="flex flex-wrap gap-2">
        {result.mode === "crawler" ? (
          <>
            <PlanChip label="최대 페이지" value={plan.max_pages} />
            <PlanChip label="탐색 깊이" value={plan.max_depth} />
          </>
        ) : (
          <PlanChip label="최대 URL" value={plan.max_items} />
        )}
        {plan.keywords.length > 0 && <PlanChip label="키워드" value={plan.keywords.join(", ")} />}
      </div>

      <div>
        <p className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">실행 결과</p>
        <dl className="mt-2 grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
          {Object.entries(summary).map(([key, value]) => (
            <div key={key} className="contents">
              <dt className="text-muted-foreground">{SUMMARY_LABELS[key] ?? key}</dt>
              <dd className="break-all font-medium text-foreground">{formatValue(value)}</dd>
            </div>
          ))}
        </dl>
      </div>
    </div>
  )
}

function PlanChip({ label, value }: { label: string; value: string | number }) {
  return (
    <span className="inline-flex items-center gap-1.5 rounded-full border border-border/60 bg-background/60 px-3 py-1 text-xs">
      <span className="text-muted-foreground">{label}</span>
      <span className="font-semibold text-foreground">{value}</span>
    </span>
  )
}

function formatValue(value: unknown): string {
  if (value === null || value === undefined || value === "") return "-"
  if (Array.isArray(value)) return value.length ? value.join(", ") : "-"
  return String(value)
}
