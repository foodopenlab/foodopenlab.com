"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Progress } from "@/components/ui/progress"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { cn } from "@/lib/utils"

const API_LABELS: Record<string, string> = {
  food_safety: "식품안전나라",
  law: "법제처",
  gemini: "Gemini AI",
  weather: "날씨",
  haccp_product: "HACCP 인증원",
}

function labelForApi(name: string) {
  return API_LABELS[name] ?? name
}

type StatItem = {
  api_name: string
  total_calls: number
  cache_hits: number
  cache_hit_rate: number
  avg_response_ms: number
  error_count: number
  error_rate: number
}

type ApiLog = {
  id: number
  api_name: string
  endpoint: string | null
  status_code: number | null
  response_ms: number | null
  is_cache_hit: boolean
  called_at: string
}

type Period = "today" | "week" | "month"

function statusTone(code: number | null) {
  if (code == null) return "text-muted-foreground"
  if (code >= 500) return "text-destructive font-medium"
  if (code >= 400) return "text-amber-500 font-medium"
  return "text-emerald-500 font-medium"
}

export default function AdminApiStatsPage() {
  const [period, setPeriod] = useState<Period>("today")
  const [stats, setStats] = useState<StatItem[]>([])
  const [statsLoading, setStatsLoading] = useState(true)
  const [logPage, setLogPage] = useState(1)
  const [logTotal, setLogTotal] = useState(0)
  const [logs, setLogs] = useState<ApiLog[]>([])
  const [logsLoading, setLogsLoading] = useState(true)
  const [apiFilter, setApiFilter] = useState<string>("")

  const loadStats = useCallback(async () => {
    setStatsLoading(true)
    try {
      const res = await adminFetch(`/admin/api-stats?period=${period}`)
      if (!res.ok) throw new Error("fail")
      const j = (await res.json()) as { stats: StatItem[] }
      setStats(j.stats ?? [])
    } catch {
      setStats([])
    } finally {
      setStatsLoading(false)
    }
  }, [period])

  const loadLogs = useCallback(async () => {
    setLogsLoading(true)
    try {
      const qs = new URLSearchParams({ page: String(logPage), size: "50" })
      if (apiFilter) qs.set("api_name", apiFilter)
      const res = await adminFetch(`/admin/logs/api?${qs}`)
      if (!res.ok) throw new Error("fail")
      const j = (await res.json()) as { total: number; items: ApiLog[] }
      setLogs(j.items ?? [])
      setLogTotal(j.total)
    } catch {
      setLogs([])
      setLogTotal(0)
    } finally {
      setLogsLoading(false)
    }
  }, [logPage, apiFilter])

  useEffect(() => {
    void loadStats()
  }, [loadStats])

  useEffect(() => {
    void loadLogs()
  }, [loadLogs])

  useEffect(() => {
    setLogPage(1)
  }, [apiFilter])

  const logPages = Math.max(1, Math.ceil(logTotal / 50))

  const periodBtn = (p: Period, label: string) => (
    <button
      type="button"
      onClick={() => setPeriod(p)}
      className={cn(
        "rounded-md px-3 py-2 text-sm font-medium",
        period === p ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted",
      )}
    >
      {label}
    </button>
  )

  return (
    <div className="space-y-10">
      <div className="flex flex-wrap gap-2 border-b border-border pb-4">
        {periodBtn("today", "오늘")}
        {periodBtn("week", "이번주")}
        {periodBtn("month", "이번달")}
      </div>

      <section>
        <h2 className="mb-3 text-sm font-medium text-muted-foreground">API별 통계</h2>
        {statsLoading ? (
          <div className="grid gap-4 md:grid-cols-3">
            {[0, 1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-36 rounded-lg" />
            ))}
          </div>
        ) : stats.length === 0 ? (
          <p className="text-sm text-muted-foreground">표시할 통계가 없습니다.</p>
        ) : (
          <div className="grid gap-4 md:grid-cols-3">
            {stats.map((s) => (
              <div key={s.api_name} className="rounded-lg border border-border bg-card p-4">
                <p className="font-semibold text-foreground">{labelForApi(s.api_name)}</p>
                <p className="mt-1 text-xs text-muted-foreground">{s.api_name}</p>
                <p className="mt-3 text-sm">
                  총 호출: <span className="font-medium">{s.total_calls}</span>회
                </p>
                <div className="mt-2 space-y-1">
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>캐시 히트율</span>
                    <span className="text-emerald-500">{s.cache_hit_rate}%</span>
                  </div>
                  <Progress value={Math.min(100, s.cache_hit_rate)} className="h-2" />
                </div>
                <p className="mt-3 text-sm text-muted-foreground">
                  평균 응답: <span className="text-foreground">{s.avg_response_ms.toFixed(0)}ms</span>
                </p>
                <p className={cn("text-sm", s.error_rate > 5 ? "text-destructive font-semibold" : "text-muted-foreground")}>
                  에러율: {s.error_rate}%
                </p>
              </div>
            ))}
          </div>
        )}
      </section>

      <section>
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <h2 className="text-sm font-medium text-muted-foreground">호출 로그</h2>
          <Select value={apiFilter || "__all__"} onValueChange={(v) => setApiFilter(v === "__all__" ? "" : v)}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="API 전체" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="__all__">API 전체</SelectItem>
              {Object.keys(API_LABELS).map((k) => (
                <SelectItem key={k} value={k}>
                  {labelForApi(k)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        {logsLoading ? (
          <div className="space-y-2">
            {[0, 1, 2, 3, 4].map((i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>API명</TableHead>
                  <TableHead>엔드포인트</TableHead>
                  <TableHead>상태코드</TableHead>
                  <TableHead>응답시간</TableHead>
                  <TableHead>캐시</TableHead>
                  <TableHead>호출시각</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {logs.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell>{labelForApi(row.api_name)}</TableCell>
                    <TableCell className="max-w-[220px] truncate font-mono text-xs text-muted-foreground">
                      {row.endpoint ?? "—"}
                    </TableCell>
                    <TableCell className={statusTone(row.status_code)}>{row.status_code ?? "—"}</TableCell>
                    <TableCell>{row.response_ms != null ? `${row.response_ms}ms` : "—"}</TableCell>
                    <TableCell>
                      {row.is_cache_hit ? (
                        <span className="text-emerald-500">HIT</span>
                      ) : (
                        <span className="text-muted-foreground">MISS</span>
                      )}
                    </TableCell>
                    <TableCell className="whitespace-nowrap text-muted-foreground text-xs">
                      {new Date(row.called_at).toLocaleString("ko-KR")}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <div className="mt-4 flex items-center justify-end gap-2">
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={logPage <= 1}
                onClick={() => setLogPage((p) => p - 1)}
              >
                이전
              </Button>
              <span className="text-sm text-muted-foreground">
                {logPage} / {logPages}
              </span>
              <Button
                type="button"
                variant="outline"
                size="sm"
                disabled={logPage >= logPages}
                onClick={() => setLogPage((p) => p + 1)}
              >
                다음
              </Button>
            </div>
          </>
        )}
      </section>
    </div>
  )
}
