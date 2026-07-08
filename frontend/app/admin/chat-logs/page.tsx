"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { ChatLogTable, type ChatSessionRow } from "@/components/admin/chat-log-table"
import { ChatLogDetailModal } from "@/components/admin/chat-log-detail-modal"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Empty, EmptyDescription, EmptyHeader, EmptyTitle } from "@/components/ui/empty"
import { cn } from "@/lib/utils"

type Stats = {
  today_total: number
  week_total: number
  all_total: number
  analysis_total: number
  ingredient_total?: number
  regulation_total: number
}

type Tab = "all" | "analysis" | "regulation"

const size = 20

export default function AdminChatLogsPage() {
  const [tab, setTab] = useState<Tab>("all")
  const [page, setPage] = useState(1)
  const [stats, setStats] = useState<Stats | null>(null)
  const [rows, setRows] = useState<ChatSessionRow[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [detailId, setDetailId] = useState<string | null>(null)
  const [detailType, setDetailType] = useState<string | null>(null)

  const chatType = tab === "all" ? undefined : tab

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const qs = new URLSearchParams({ page: String(page), size: String(size) })
      if (chatType) qs.set("chat_type", chatType)
      const [resStats, resList] = await Promise.all([
        adminFetch("/admin/chat-logs/stats"),
        adminFetch(`/admin/chat-logs?${qs}`),
      ])
      if (resStats.ok) setStats((await resStats.json()) as Stats)
      if (resList.ok) {
        const j = (await resList.json()) as { total: number; items: ChatSessionRow[] }
        setRows(j.items)
        setTotal(j.total)
      } else {
        setRows([])
        setTotal(0)
      }
    } catch {
      setStats(null)
      setRows([])
      setTotal(0)
    } finally {
      setLoading(false)
    }
  }, [page, chatType])

  useEffect(() => {
    setPage(1)
  }, [tab])

  useEffect(() => {
    void load()
  }, [load])

  const totalPages = Math.max(1, Math.ceil(total / size))

  const tabBtn = (key: Tab, label: string) => (
    <button
      type="button"
      onClick={() => setTab(key)}
      className={cn(
        "rounded-md px-3 py-2 text-sm font-medium",
        tab === key ? "bg-primary text-primary-foreground" : "text-muted-foreground hover:bg-muted",
      )}
    >
      {label}
    </button>
  )

  return (
    <div className="space-y-8">
      {stats ? (
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">오늘 전체 채팅</p>
            <p className="text-2xl font-semibold">{stats.today_total}건</p>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">원료 분석</p>
            <p className="text-2xl font-semibold">{stats.analysis_total ?? stats.ingredient_total ?? 0}건</p>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">법규 채팅</p>
            <p className="text-2xl font-semibold">{stats.regulation_total}건</p>
          </div>
          <div className="rounded-lg border border-border bg-card p-4">
            <p className="text-xs text-muted-foreground">전체 누적</p>
            <p className="text-2xl font-semibold">{stats.all_total}건</p>
          </div>
        </div>
      ) : loading ? (
        <div className="grid gap-3 sm:grid-cols-2">
          {[0, 1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-24 rounded-lg" />
          ))}
        </div>
      ) : null}

      <div className="flex flex-wrap gap-2 border-b border-border pb-4">
        {tabBtn("all", "전체")}
        {tabBtn("analysis", "원료 분석")}
        {tabBtn("regulation", "법규 채팅")}
      </div>

      {loading ? (
        <div className="space-y-2">
          {[0, 1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      ) : rows.length === 0 ? (
        <Empty>
          <EmptyHeader>
            <EmptyTitle>조회된 채팅이 없습니다</EmptyTitle>
            <EmptyDescription>필터를 바꿔 다시 시도해 보세요.</EmptyDescription>
          </EmptyHeader>
        </Empty>
      ) : (
        <ChatLogTable
          rows={rows}
          onOpenDetail={(id, chatType) => {
            setDetailId(id)
            setDetailType(chatType)
          }}
        />
      )}

      <div className="flex items-center justify-end gap-2">
        <Button type="button" variant="outline" size="sm" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
          이전
        </Button>
        <span className="text-sm text-muted-foreground">
          {page} / {totalPages}
        </span>
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={page >= totalPages}
          onClick={() => setPage((p) => p + 1)}
        >
          다음
        </Button>
      </div>

      <ChatLogDetailModal
        sessionId={detailId}
        chatType={detailType}
        open={detailId != null}
        onClose={() => {
          setDetailId(null)
          setDetailType(null)
        }}
      />
    </div>
  )
}
