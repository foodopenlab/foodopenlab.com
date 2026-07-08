"use client"

import { useEffect, useState } from "react"
import { SkeletonCard } from "@/components/common/skeleton-card"
import { Badge } from "@/components/ui/badge"
import type { LicenseStatusSearchResponse } from "@/lib/types/phase3"
import { cn } from "@/lib/utils"

function statusBadgeClass(status: string) {
  switch (status) {
    case "영업중":
      return "bg-green-100 text-green-700 dark:bg-green-950/40 dark:text-green-300"
    case "휴업":
      return "bg-orange-100 text-orange-700 dark:bg-orange-950/40 dark:text-orange-200"
    case "폐업":
      return "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300"
    default:
      return "bg-muted text-muted-foreground"
  }
}

type LicensePanelProps = {
  businessName: string
}

export function LicensePanel({ businessName }: LicensePanelProps) {
  const [data, setData] = useState<LicenseStatusSearchResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [fetchError, setFetchError] = useState(false)

  useEffect(() => {
    let cancelled = false
    const t = window.setTimeout(() => {
      void (async () => {
        setLoading(true)
        setFetchError(false)
        const q = new URLSearchParams({ business_name: businessName.trim() })
        try {
          const res = await fetch(`/api/license-status/search?${q.toString()}`, { cache: "no-store" })
          if (!res.ok) {
            if (!cancelled) {
              setFetchError(true)
              setLoading(false)
            }
            return
          }
          const json = (await res.json()) as LicenseStatusSearchResponse
          if (!cancelled) {
            setData(json)
            setLoading(false)
          }
        } catch {
          if (!cancelled) {
            setFetchError(true)
            setLoading(false)
          }
        }
      })()
    }, 500)
    return () => {
      cancelled = true
      window.clearTimeout(t)
    }
  }, [businessName])

  return (
    <aside className="rounded-2xl border border-border/70 bg-card/60 p-4 md:p-5">
      <div className="mb-3 flex flex-wrap items-center gap-2">
        <h2 className="text-base font-semibold text-foreground">인허가 현황</h2>
        <Badge variant="secondary" className="text-[10px]">
          식의약데이터포털 기반
        </Badge>
      </div>

      {loading ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : fetchError ? (
        <p className="text-sm text-destructive">조회 실패</p>
      ) : !data || !data.found || data.items.length === 0 ? (
        <p className="text-sm text-muted-foreground">조회된 인허가 정보가 없습니다.</p>
      ) : (
        <ul className="max-h-[480px] space-y-3 overflow-y-auto pr-1">
          {data.items.map((row, idx) => (
            <li key={`${row.license_number ?? row.business_name}-${idx}`} className="rounded-lg border border-border/60 bg-background/50 p-3">
              <p className="font-medium text-foreground">{row.business_name}</p>
              <Badge className={cn("mt-2 text-[10px]", statusBadgeClass(row.status))}>{row.status}</Badge>
              {row.business_type ? <p className="mt-1 text-xs text-muted-foreground">{row.business_type}</p> : null}
              {row.license_number ? <p className="mt-1 text-xs text-muted-foreground">허가번호 {row.license_number}</p> : null}
              {row.address ? (
                <p className="mt-1 truncate text-xs text-muted-foreground" title={row.address}>
                  {row.address}
                </p>
              ) : null}
              {row.last_changed_date ? (
                <p className="mt-1 text-xs text-muted-foreground">최종변경 {row.last_changed_date}</p>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </aside>
  )
}
