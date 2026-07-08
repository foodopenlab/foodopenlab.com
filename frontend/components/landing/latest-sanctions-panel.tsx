"use client"

import { useEffect, useState } from "react"
import { ExternalLink, Gavel, RefreshCw } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { apiPath, formatApiClientError } from "@/lib/api-path"
import { cn } from "@/lib/utils"

type SanctionItem = {
  business_name: string
  industry: string
  disposition_date: string
  disposition_start?: string
  disposition_type: string
  violation: string
  address: string
  representative: string
  disposition_detail: string
  agency: string
  serial_no: string
  category: string
  service_id: string
}

type SanctionsPayload = {
  items: SanctionItem[]
  fetched_at: string | null
  query_date: string | null
  is_today: boolean
  matched_date: string | null
  source: string
}

const SANCTIONS_API_URL = apiPath("sanctions/latest")

function formatDispositionDate(value: string) {
  if (!value) return ""
  const digits = value.replace(/\D/g, "")
  if (digits.length >= 8) {
    return `${digits.slice(0, 4)}-${digits.slice(4, 6)}-${digits.slice(6, 8)}`
  }
  return value.length >= 10 ? value.slice(0, 10) : value
}

async function fetchSanctionsPayload(): Promise<SanctionsPayload> {
  const res = await fetch(SANCTIONS_API_URL, {
    cache: "no-store",
    signal: AbortSignal.timeout(15_000),
  })
  const raw = await res.text()
  let body: (SanctionsPayload & { detail?: string }) | null = null

  if (raw.trim()) {
    try {
      body = JSON.parse(raw) as SanctionsPayload & { detail?: string }
    } catch {
      throw new Error(
        res.ok
          ? "서버 응답 형식이 올바르지 않습니다."
          : raw.slice(0, 120) || `행정처분 정보를 불러오지 못했습니다. (HTTP ${res.status})`,
      )
    }
  }

  if (!res.ok) {
    const detail = body?.detail || raw.slice(0, 200) || `행정처분 정보를 불러오지 못했습니다. (HTTP ${res.status})`
    throw new Error(formatApiClientError(detail))
  }

  return {
    items: body?.items ?? [],
    fetched_at: body?.fetched_at ?? null,
    query_date: body?.query_date ?? null,
    is_today: body?.is_today ?? false,
    matched_date: body?.matched_date ?? null,
    source: body?.source ?? "식품안전나라",
  }
}

export function LatestSanctionsPanel({
  className,
  compact = false,
}: {
  className?: string
  compact?: boolean
}) {
  const [data, setData] = useState<SanctionsPayload | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false

    fetchSanctionsPayload()
      .then((payload) => {
        if (!cancelled) {
          setData(payload)
          setError(null)
        }
      })
      .catch((e) => {
        if (!cancelled) {
          const msg = formatApiClientError(e instanceof Error ? e.message : "오류가 발생했습니다.")
          setError(
            msg.includes("timeout") || msg.includes("aborted")
              ? "백엔드(8000) 응답이 지연되었습니다. uvicorn 실행 후 새로고침해 주세요."
              : msg.includes("Failed to fetch") || msg.includes("ECONNRESET")
                ? "API 서버에 연결하지 못했습니다. BACKEND_URL(배포) 또는 로컬 uvicorn(127.0.0.1:8000)을 확인해 주세요."
                : msg,
          )
        }
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  return (
    <div
      className={cn(
        "w-full rounded-2xl border border-border/80 bg-card/60 text-left shadow-sm backdrop-blur-sm",
        compact ? "p-4 md:p-5" : "p-4 md:p-5",
        className,
      )}
    >
      <div className="mb-3 flex flex-wrap items-start justify-between gap-2 sm:items-center">
        <div className="flex min-w-0 flex-1 flex-wrap items-center gap-2">
          <Gavel className="h-4 w-4 shrink-0 text-rose-500" />
          <h2 className="text-base font-semibold text-foreground">행정처분결과</h2>
          <Badge variant="secondary" className="text-xs">
            식품안전나라
          </Badge>
        </div>
        {data?.is_today && data.query_date ? (
          <span className="w-full shrink-0 text-xs text-muted-foreground sm:w-auto sm:text-sm">처분확정일 오늘 {data.query_date}</span>
        ) : data?.matched_date ? (
          <span className="w-full shrink-0 text-xs text-muted-foreground sm:w-auto sm:text-sm">처분확정일 {data.matched_date}</span>
        ) : null}
      </div>

      {loading ? (
        <div className="flex items-center gap-2 py-6 text-base text-muted-foreground">
          <RefreshCw className="h-4 w-4 animate-spin" />
          행정처분 정보 불러오는 중…
        </div>
      ) : error ? (
        <p className="py-4 text-sm text-destructive">{error}</p>
      ) : !data?.items?.length ? (
        <p className="py-4 text-sm text-muted-foreground">행정처분 정보를 찾을 수 없습니다.</p>
      ) : (
        <ul className="space-y-3">
          {!data.is_today ? (
            <p className="text-sm text-muted-foreground">
              오늘 처분확정일인 건이 없어, 가장 최근 처분확정일 기준 1건을 표시합니다.
            </p>
          ) : null}
          {data.items.slice(0, 1).map((item) => (
            <li
              key={item.serial_no || `${item.business_name}-${item.disposition_date}`}
              className="rounded-xl border border-border/60 bg-background/50 px-3 py-3 md:px-4"
            >
              <div className="flex flex-wrap items-start justify-between gap-2">
                <p className="text-base font-medium text-foreground">{item.business_name}</p>
                <div className="flex shrink-0 flex-wrap gap-1">
                  {item.category ? (
                    <Badge variant="secondary" className="text-xs">
                      {item.category}
                    </Badge>
                  ) : null}
                  {item.disposition_type ? (
                    <Badge variant="outline" className="text-xs">
                      {item.disposition_type}
                    </Badge>
                  ) : null}
                </div>
              </div>
              <p className="mt-1 line-clamp-2 text-sm text-muted-foreground sm:text-base">
                {item.violation || item.disposition_detail}
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                {item.industry}
                {item.address ? ` · ${item.address}` : ""}
                {item.disposition_date ? ` · 처분확정 ${formatDispositionDate(item.disposition_date)}` : ""}
                {item.disposition_start
                  ? ` · 처분시작 ${formatDispositionDate(item.disposition_start)}`
                  : ""}
              </p>
              {item.agency ? (
                <p className="mt-1 text-xs text-muted-foreground">{item.agency}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}

      <a
        href="https://www.foodsafetykorea.go.kr/api/openApiInfo.do?svc_no=I0470"
        target="_blank"
        rel="noopener noreferrer"
        className="mt-4 inline-flex items-center gap-1 text-xs text-primary hover:underline"
      >
        식품안전나라에서 더 보기
        <ExternalLink className="h-3 w-3" />
      </a>
    </div>
  )
}
