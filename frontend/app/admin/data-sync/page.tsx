"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { RefreshCw, Database, FileText, CheckCircle2, AlertCircle } from "lucide-react"

type SyncStatus = {
  recalls_db_count: number
  enforcements_db_count: number
  recall_cache_last_updated: string | null
  sanction_cache_last_updated: string | null
  last_sync_at: string | null
  sync_wave: string | null
  sync_slot: string | null
}

const SYNC_WAVE_LABEL: Record<string, string> = {
  morning: "오전",
  afternoon: "오후",
  manual: "수동",
}

export default function AdminDataSyncPage() {
  const [status, setStatus] = useState<SyncStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [syncingRecalls, setSyncingRecalls] = useState(false)
  const [syncingEnforcements, setSyncingEnforcements] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMsg, setSuccessMsg] = useState<string | null>(null)

  const loadStatus = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminFetch("/admin/data-sync/status")
      if (!res.ok) throw new Error("동기화 상태를 가져오는데 실패했습니다.")
      const data = (await res.json()) as SyncStatus
      setStatus(data)
    } catch (err: any) {
      setError(err.message || "상태 로딩 실패")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadStatus()
  }, [loadStatus])

  const triggerSync = async (type: "recalls" | "enforcements") => {
    if (type === "recalls") setSyncingRecalls(true)
    else setSyncingEnforcements(true)
    
    setError(null)
    setSuccessMsg(null)

    try {
      const res = await adminFetch("/admin/data-sync/trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sync_type: type }),
      })
      if (!res.ok) throw new Error("API 동기화 요청이 실패했습니다.")
      const data = (await res.json()) as { started?: boolean; message?: string }

      setSuccessMsg(data.message ?? "동기화 요청을 보냈습니다.")
      void loadStatus()
    } catch (err: any) {
      setError(err.message || "동기화 중 오류가 발생했습니다.")
    } finally {
      if (type === "recalls") setSyncingRecalls(false)
      else setSyncingEnforcements(false)
    }
  }

  const formatTime = (isoString: string | null) => {
    if (!isoString) return "캐시 파일 없음"
    return new Date(isoString).toLocaleString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    })
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">공공데이터 동기화 관리</h1>
          <p className="text-sm text-muted-foreground">
            식품안전나라 공공 API의 회수 정보 및 행정처분 캐시 상태를 모니터링하고 즉시 동기화합니다.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => void loadStatus()}
          disabled={loading || syncingRecalls || syncingEnforcements}
          className="gap-2"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} />
          새로고침
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-lg border border-destructive/20 bg-destructive/10 p-4 text-sm text-destructive">
          <AlertCircle className="size-5 shrink-0" />
          <div>{error}</div>
        </div>
      )}

      {successMsg && (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-500">
          <CheckCircle2 className="size-5 shrink-0" />
          <div>{successMsg}</div>
        </div>
      )}

      {status && (
        <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-4 text-sm">
          <CheckCircle2 className="size-5 shrink-0 text-primary" />
          <div>
            <span className="font-semibold text-foreground">마지막 동기화</span>
            <span className="ml-2 text-muted-foreground">
              {status.last_sync_at
                ? `${formatTime(status.last_sync_at)} (${SYNC_WAVE_LABEL[status.sync_wave ?? ""] ?? status.sync_wave ?? "-"} · ${status.sync_slot ?? "-"})`
                : "동기화 기록 없음"}
            </span>
          </div>
        </div>
      )}

      {loading && !status ? (
        <div className="grid gap-6 md:grid-cols-2">
          <Skeleton className="h-64 rounded-xl" />
          <Skeleton className="h-64 rounded-xl" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Recalls Sync Section */}
          <div className="relative overflow-hidden rounded-xl border border-border bg-card p-6 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-6">
              <div className="space-y-1">
                <h2 className="text-lg font-semibold">식품 회수 정보 동기화</h2>
                <p className="text-xs text-muted-foreground">식품안전나라 회수 제품 공공 데이터</p>
              </div>
              <div className="rounded-lg bg-primary/10 p-2.5 text-primary">
                <Database className="size-6" />
              </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex justify-between border-b border-border/50 pb-2.5 text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <Database className="size-4 text-muted-foreground/75" />
                  로컬 DB 누적 건수
                </span>
                <span className="font-semibold text-foreground text-base">
                  {status?.recalls_db_count.toLocaleString() ?? 0} 건
                </span>
              </div>
              <div className="flex justify-between pb-1.5 text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <FileText className="size-4 text-muted-foreground/75" />
                  JSON 디스크 캐시 갱신일
                </span>
                <span className="font-medium text-foreground">
                  {formatTime(status?.recall_cache_last_updated ?? null)}
                </span>
              </div>
            </div>

            <Button
              className="w-full gap-2 shadow-sm font-medium"
              onClick={() => void triggerSync("recalls")}
              disabled={syncingRecalls || syncingEnforcements}
            >
              <RefreshCw className={`size-4 ${syncingRecalls ? "animate-spin" : ""}`} />
              {syncingRecalls ? "동기화 갱신 중..." : "즉시 동기화 진행"}
            </Button>
          </div>

          {/* Enforcements Sync Section */}
          <div className="relative overflow-hidden rounded-xl border border-border bg-card p-6 shadow-sm transition-all hover:shadow-md">
            <div className="flex items-center justify-between mb-6">
              <div className="space-y-1">
                <h2 className="text-lg font-semibold">행정처분 내역 동기화</h2>
                <p className="text-xs text-muted-foreground">식품안전나라 기업 영업소 행정처분 공공 데이터</p>
              </div>
              <div className="rounded-lg bg-amber-500/10 p-2.5 text-amber-500">
                <Database className="size-6" />
              </div>
            </div>

            <div className="space-y-4 mb-8">
              <div className="flex justify-between border-b border-border/50 pb-2.5 text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <Database className="size-4 text-muted-foreground/75" />
                  로컬 DB 누적 건수
                </span>
                <span className="font-semibold text-foreground text-base">
                  {status?.enforcements_db_count.toLocaleString() ?? 0} 건
                </span>
              </div>
              <div className="flex justify-between pb-1.5 text-sm">
                <span className="text-muted-foreground flex items-center gap-1.5">
                  <FileText className="size-4 text-muted-foreground/75" />
                  JSON 디스크 캐시 갱신일
                </span>
                <span className="font-medium text-foreground">
                  {formatTime(status?.sanction_cache_last_updated ?? null)}
                </span>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full gap-2 border-amber-500/30 text-amber-500 hover:bg-amber-500/10 shadow-sm font-medium"
              onClick={() => void triggerSync("enforcements")}
              disabled={syncingRecalls || syncingEnforcements}
            >
              <RefreshCw className={`size-4 ${syncingEnforcements ? "animate-spin" : ""}`} />
              {syncingEnforcements ? "동기화 갱신 중..." : "즉시 동기화 진행"}
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
