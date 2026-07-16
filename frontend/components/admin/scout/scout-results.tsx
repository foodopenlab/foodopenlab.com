"use client"

import { useCallback, useEffect, useState } from "react"
import { ExternalLink, RefreshCw } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { adminFetch } from "@/lib/admin/auth"

type Kind = "crawled" | "scraped"
type Status = "idle" | "loading" | "error"

type Row = {
  url?: string
  title?: string
  matched_keywords?: string[]
  snippet?: string
  content_length?: number
  saved_at?: number
}

type ResultsResponse = {
  kind: Kind
  count: number
  items: Row[]
  detail?: string
}

const KIND_META: Record<Kind, { title: string; desc: string }> = {
  crawled: {
    title: "크롤러 결과",
    desc: "크롤러가 찾은 관련 URL 목록 (resources/crawled/crawled.jsonl)",
  },
  scraped: {
    title: "스크래퍼 결과",
    desc: "스크래퍼가 저장한 페이지 본문 (resources/scraped/scraped.jsonl)",
  },
}

export function ScoutResults() {
  const [kind, setKind] = useState<Kind>("crawled")
  const [rows, setRows] = useState<Row[]>([])
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")

  const load = useCallback(async (target: Kind) => {
    setStatus("loading")
    setMessage("")
    try {
      const res = await adminFetch(`/admin/scout/results?kind=${target}&limit=200`)
      const data = (await res.json().catch(() => ({}))) as ResultsResponse
      if (res.ok && Array.isArray(data.items)) {
        setRows(data.items)
        setStatus("idle")
      } else {
        setRows([])
        setStatus("error")
        setMessage(data.detail ?? "결과를 불러오지 못했습니다.")
      }
    } catch {
      setRows([])
      setStatus("error")
      setMessage("네트워크 오류가 발생했습니다.")
    }
  }, [])

  useEffect(() => {
    void load(kind)
  }, [kind, load])

  function switchKind(next: string) {
    setKind(next as Kind)
  }

  const meta = KIND_META[kind]

  return (
    <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
      <CardHeader>
        <div className="flex items-start justify-between gap-4">
          <div>
            <CardTitle>{meta.title}</CardTitle>
            <CardDescription>{meta.desc}</CardDescription>
          </div>
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="gap-2"
            onClick={() => void load(kind)}
            disabled={status === "loading"}
          >
            <RefreshCw className={`h-4 w-4 ${status === "loading" ? "animate-spin" : ""}`} />
            새로고침
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        <Tabs value={kind} onValueChange={switchKind}>
          <TabsList className="grid w-full grid-cols-2">
            <TabsTrigger value="crawled">크롤러</TabsTrigger>
            <TabsTrigger value="scraped">스크래퍼</TabsTrigger>
          </TabsList>
        </Tabs>

        {status === "error" && message ? (
          <p className="py-8 text-center text-sm font-medium text-destructive">{message}</p>
        ) : status === "loading" ? (
          <p className="py-8 text-center text-sm text-muted-foreground">불러오는 중…</p>
        ) : rows.length === 0 ? (
          <p className="py-8 text-center text-sm text-muted-foreground">
            아직 저장된 결과가 없습니다. 크롤러/스크래퍼를 실행해 보세요.
          </p>
        ) : (
          <>
            <p className="text-xs text-muted-foreground">총 {rows.length}건 (최신순)</p>
            <div className="overflow-x-auto rounded-lg border border-border/60">
              {kind === "crawled" ? <CrawledTable rows={rows} /> : <ScrapedTable rows={rows} />}
            </div>
          </>
        )}
      </CardContent>
    </Card>
  )
}

function CrawledTable({ rows }: { rows: Row[] }) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="bg-muted/40 text-xs uppercase tracking-wider text-muted-foreground">
        <tr>
          <Th>저장 시각</Th>
          <Th>URL</Th>
          <Th>제목</Th>
          <Th>매칭 키워드</Th>
        </tr>
      </thead>
      <tbody className="divide-y divide-border/50">
        {rows.map((r, i) => (
          <tr key={i} className="align-top">
            <Td className="whitespace-nowrap text-muted-foreground">{formatTime(r.saved_at)}</Td>
            <Td><UrlLink url={r.url} /></Td>
            <Td>{r.title || "-"}</Td>
            <Td>{r.matched_keywords?.length ? r.matched_keywords.join(", ") : "-"}</Td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function ScrapedTable({ rows }: { rows: Row[] }) {
  return (
    <table className="w-full text-left text-sm">
      <thead className="bg-muted/40 text-xs uppercase tracking-wider text-muted-foreground">
        <tr>
          <Th>저장 시각</Th>
          <Th>URL</Th>
          <Th>제목</Th>
          <Th>길이</Th>
          <Th>스니펫</Th>
        </tr>
      </thead>
      <tbody className="divide-y divide-border/50">
        {rows.map((r, i) => (
          <tr key={i} className="align-top">
            <Td className="whitespace-nowrap text-muted-foreground">{formatTime(r.saved_at)}</Td>
            <Td><UrlLink url={r.url} /></Td>
            <Td>{r.title || "-"}</Td>
            <Td className="whitespace-nowrap tabular-nums text-muted-foreground">
              {typeof r.content_length === "number" ? r.content_length.toLocaleString() : "-"}
            </Td>
            <Td className="min-w-[16rem] max-w-[28rem] text-muted-foreground">{r.snippet || "-"}</Td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}

function Th({ children }: { children: React.ReactNode }) {
  return <th className="px-3 py-2 font-semibold">{children}</th>
}

function Td({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  return <td className={`px-3 py-2 ${className}`}>{children}</td>
}

function UrlLink({ url }: { url?: string }) {
  if (!url) return <>-</>
  return (
    <a
      href={url}
      target="_blank"
      rel="noopener noreferrer"
      className="inline-flex items-center gap-1 break-all text-primary hover:underline"
    >
      <span className="break-all">{url}</span>
      <ExternalLink className="h-3 w-3 shrink-0" aria-hidden />
    </a>
  )
}

function formatTime(sec?: number): string {
  if (typeof sec !== "number" || !Number.isFinite(sec)) return "-"
  return new Date(sec * 1000).toLocaleString("ko-KR", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  })
}
