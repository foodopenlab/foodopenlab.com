"use client"

import { useEffect, useMemo, useState } from "react"
import { Activity, BarChart3, RefreshCw, Users } from "lucide-react"
import { apiPath, formatApiClientError } from "@/lib/api-path"
import { cn } from "@/lib/utils"

type YearlyRow = {
  year: string
  total_incidents: number
  total_patients: number
}

type YearlyPayload = {
  data: YearlyRow[]
}

const FOOD_STATS_YEARLY_URL = apiPath("food-stats/yearly")

function formatCount(n: number) {
  return n.toLocaleString("ko-KR")
}

type FoodPoisoningStatsPanelProps = {
  className?: string
  /** 히어로 채팅 아래 남는 영역을 채우는 카드 스타일 */
  variant?: "compact" | "hero"
}

export function FoodPoisoningStatsPanel({ className, variant = "hero" }: FoodPoisoningStatsPanelProps) {
  const [rows, setRows] = useState<YearlyRow[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isHero = variant === "hero"

  useEffect(() => {
    let cancelled = false

    fetch(FOOD_STATS_YEARLY_URL, { cache: "no-store", signal: AbortSignal.timeout(15_000) })
      .then(async (res) => {
        const raw = await res.text()
        let body: YearlyPayload | null = null
        if (raw.trim()) {
          try {
            body = JSON.parse(raw) as YearlyPayload
          } catch {
            throw new Error(res.ok ? "응답 형식 오류" : raw.slice(0, 80) || `HTTP ${res.status}`)
          }
        }
        if (!res.ok) {
          throw new Error(formatApiClientError(raw.slice(0, 200) || `통계를 불러오지 못했습니다. (HTTP ${res.status})`))
        }
        if (!cancelled) {
          const sorted = [...(body?.data ?? [])].sort((a, b) => b.year.localeCompare(a.year))
          setRows(sorted.slice(0, 4))
          setError(null)
        }
      })
      .catch((e) => {
        if (!cancelled) {
          setRows([])
          setError(formatApiClientError(e instanceof Error ? e.message : "통계 로드 실패"))
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  const maxIncidents = useMemo(
    () => Math.max(...rows.map((r) => r.total_incidents), 1),
    [rows],
  )

  const latest = rows[0]

  return (
    <section
      className={cn(
        "flex min-w-0 flex-col",
        isHero &&
          "min-h-[12rem] flex-1 rounded-2xl border border-primary/15 bg-gradient-to-br from-card/90 via-card/60 to-primary/10 p-5 shadow-sm backdrop-blur-sm sm:min-h-[14rem] sm:p-6 lg:min-h-0",
        !isHero && "rounded-xl border border-border/80 bg-secondary/20 px-3 py-2.5",
        className,
      )}
      aria-label="식중독 통계"
    >
      <div
        className={cn(
          "flex flex-wrap items-start justify-between gap-3",
          isHero ? "mb-4 border-b border-border/50 pb-3" : "mb-2",
        )}
      >
        <div className="flex min-w-0 items-center gap-2">
          <div
            className={cn(
              "flex shrink-0 items-center justify-center rounded-lg bg-primary/15 text-primary",
              isHero ? "h-10 w-10 sm:h-11 sm:w-11" : "h-7 w-7",
            )}
          >
            <BarChart3 className={isHero ? "h-5 w-5 sm:h-6 sm:w-6" : "h-3.5 w-3.5"} aria-hidden />
          </div>
          <div className="min-w-0 text-left">
            <h3 className={cn("font-semibold text-foreground", isHero ? "text-base sm:text-lg" : "text-xs sm:text-sm")}>
              식중독 통계
            </h3>
            <p className={cn("text-muted-foreground", isHero ? "text-sm sm:text-base" : "text-[10px]")}>
              식의약 안전정보원 · 연도별 발생·환자 수
            </p>
          </div>
        </div>
        {isHero && latest && !loading && !error ? (
          <div className="rounded-lg border border-primary/20 bg-primary/10 px-3 py-2 text-right sm:px-4">
            <p className="text-xs font-medium text-primary sm:text-sm">최근({latest.year})</p>
            <p className="text-base font-semibold tabular-nums text-foreground sm:text-lg">
              {formatCount(latest.total_incidents)}건 · {formatCount(latest.total_patients)}명
            </p>
          </div>
        ) : null}
      </div>

      {loading ? (
        <div className="flex flex-1 items-center justify-center gap-2 py-6 text-base text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          통계 불러오는 중…
        </div>
      ) : error ? (
        <p className="flex flex-1 items-center text-sm text-destructive">{error}</p>
      ) : rows.length === 0 ? (
        <p className="flex flex-1 items-center text-sm text-muted-foreground">표시할 통계가 없습니다.</p>
      ) : (
        <ul
          className={cn(
            "grid flex-1 gap-3",
            isHero ? "grid-cols-2 lg:grid-cols-4" : "grid-cols-2 sm:grid-cols-4",
          )}
        >
          {rows.map((row) => {
            const barPct = Math.round((row.total_incidents / maxIncidents) * 100)
            return (
              <li
                key={row.year}
                className={cn(
                  "flex flex-col rounded-xl border border-border/60 bg-background/50 text-left",
                  isHero ? "min-h-[6.5rem] justify-between px-3 py-3.5 sm:min-h-[7rem] sm:px-4 sm:py-4" : "px-2 py-1.5",
                )}
              >
                <div className="flex items-center justify-between gap-2">
                  <p className={cn("font-semibold text-foreground", isHero ? "text-base sm:text-lg" : "text-[10px]")}>
                    {row.year}년
                  </p>
                  {isHero ? (
                    <span className="text-xs tabular-nums text-muted-foreground sm:text-sm">{barPct}%</span>
                  ) : null}
                </div>
                {isHero ? (
                  <div
                    className="my-2.5 h-2 overflow-hidden rounded-full bg-secondary sm:my-3"
                    role="presentation"
                    aria-hidden
                  >
                    <div
                      className="h-full rounded-full bg-primary/80 transition-all"
                      style={{ width: `${barPct}%` }}
                    />
                  </div>
                ) : null}
                <div className={cn("space-y-0.5", isHero && "mt-auto")}>
                  <p className={cn("flex items-center gap-1.5 text-foreground", isHero ? "text-sm sm:text-base" : "text-xs")}>
                    <Activity className={cn("shrink-0 text-amber-500/90", isHero ? "h-4 w-4" : "h-3 w-3")} aria-hidden />
                    발생{" "}
                    <span className={cn("font-semibold tabular-nums", isHero && "text-base sm:text-lg")}>
                      {formatCount(row.total_incidents)}
                    </span>
                    건
                  </p>
                  <p
                    className={cn(
                      "flex items-center gap-1.5 text-muted-foreground",
                      isHero ? "text-sm sm:text-base" : "text-[11px]",
                    )}
                  >
                    <Users className={cn("shrink-0 opacity-70", isHero ? "h-4 w-4" : "h-3 w-3")} aria-hidden />
                    환자{" "}
                    <span className={cn("tabular-nums font-medium text-foreground", isHero && "text-base sm:text-lg")}>
                      {formatCount(row.total_patients)}
                    </span>
                    명
                  </p>
                </div>
              </li>
            )
          })}
        </ul>
      )}
    </section>
  )
}
