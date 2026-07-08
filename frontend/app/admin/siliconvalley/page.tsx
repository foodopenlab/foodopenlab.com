"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { Cpu, Network, RefreshCw, Server, Users } from "lucide-react"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"
import {
  fetchPiperStatuses,
  type PiperCharacterStatus,
} from "@/lib/admin/siliconvalley-client"
import { AdminKpiCard } from "@/components/admin/admin-kpi-card"
import { AdminPanelCard } from "@/components/admin/admin-panel-card"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { cn } from "@/lib/utils"

const ROLE_COLORS = ["oklch(0.72 0.17 160)", "oklch(0.828 0.189 84.429)", "oklch(0.6 0.118 184.704)"]

function PiperStatusCard({ row }: { row: PiperCharacterStatus }) {
  return (
    <div className="rounded-xl border border-border/60 bg-muted/20 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0">
          <p className="font-semibold text-foreground">{row.label}</p>
          <p className="mt-0.5 text-xs text-muted-foreground">{row.role}</p>
        </div>
        <span
          className={cn(
            "shrink-0 rounded-full px-2 py-0.5 text-[11px] font-semibold",
            row.online
              ? "bg-emerald-500/15 text-emerald-500"
              : "bg-destructive/15 text-destructive",
          )}
        >
          {row.online ? "온라인" : "오프라인"}
        </span>
      </div>
      <p className="mt-3 truncate text-xs text-muted-foreground">
        {row.online ? row.name : row.error ?? "—"}
      </p>
    </div>
  )
}

export default function AdminSiliconValleyPage() {
  const [rows, setRows] = useState<PiperCharacterStatus[]>([])
  const [loading, setLoading] = useState(true)
  const [err, setErr] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setErr(null)
    try {
      setRows(await fetchPiperStatuses())
    } catch {
      setErr("Piper API 상태를 불러올 수 없습니다.")
      setRows([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const onlineCount = rows.filter((row) => row.online).length
  const readiness = rows.length ? (onlineCount / rows.length) * 100 : 0

  const roleDonut = useMemo(() => {
    const counts = new Map<string, number>()
    for (const row of rows) {
      counts.set(row.role, (counts.get(row.role) ?? 0) + 1)
    }
    return Array.from(counts.entries()).map(([name, value]) => ({ name, value }))
  }, [rows])

  if (loading) {
    return (
      <div className="space-y-4 sm:space-y-6">
        <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
          {[0, 1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-28 rounded-2xl sm:h-32" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <Skeleton className="h-72 rounded-2xl lg:col-span-2 sm:h-96" />
          <Skeleton className="h-72 rounded-2xl sm:h-96" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-4 sm:space-y-6">
      {err ? (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200">
          {err}
        </div>
      ) : null}

      <div className="grid grid-cols-2 gap-3 sm:gap-4 lg:grid-cols-4">
        <AdminKpiCard
          title="Piper 크루"
          value={String(rows.length)}
          delta="등록 캐릭터"
          deltaTone="neutral"
          icon={Users}
        />
        <AdminKpiCard
          title="온라인"
          value={String(onlineCount)}
          delta={`${readiness.toFixed(0)}% 가동`}
          deltaTone="up"
          icon={Network}
        />
        <AdminKpiCard
          title="백엔드"
          value="FastAPI"
          delta="siliconvalley"
          deltaTone="neutral"
          icon={Server}
        />
        <AdminKpiCard
          title="프로젝트"
          value="Piper"
          delta="/api/piper"
          deltaTone="up"
          icon={Cpu}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <AdminPanelCard
          title="Piper 캐릭터"
          subtitle="introduce_myself API 상태"
          className="lg:col-span-2"
          action={
            <Button type="button" variant="outline" size="sm" className="h-9 gap-1.5" onClick={() => void load()}>
              <RefreshCw className="size-3.5" aria-hidden />
              새로고침
            </Button>
          }
        >
          <div className="space-y-3 md:hidden">
            {rows.map((row) => (
              <PiperStatusCard key={row.key} row={row} />
            ))}
          </div>

          <div className="hidden overflow-x-auto md:block">
            <Table className="min-w-[520px]">
              <TableHeader>
                <TableRow>
                  <TableHead>캐릭터</TableHead>
                  <TableHead>역할</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>응답</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.key}>
                    <TableCell className="font-medium">{row.label}</TableCell>
                    <TableCell>{row.role}</TableCell>
                    <TableCell>
                      <span
                        className={cn(
                          "text-xs font-semibold",
                          row.online ? "text-emerald-500" : "text-destructive",
                        )}
                      >
                        {row.online ? "온라인" : "오프라인"}
                      </span>
                    </TableCell>
                    <TableCell className="max-w-xs truncate text-muted-foreground">
                      {row.online ? row.name : row.error ?? "—"}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </AdminPanelCard>

        <AdminPanelCard title="역할 분포" subtitle="캐릭터 역할 구성">
          <div className="h-44 sm:h-52">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={roleDonut} dataKey="value" innerRadius={42} outerRadius={68} paddingAngle={4}>
                  {roleDonut.map((_, index) => (
                    <Cell key={index} fill={ROLE_COLORS[index % ROLE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="mt-3 space-y-2">
            {rows.map((row) => (
              <div key={row.key}>
                <div className="mb-1 flex justify-between text-xs text-muted-foreground">
                  <span className="truncate pr-2">{row.label}</span>
                  <span className="shrink-0">{row.online ? "100%" : "0%"}</span>
                </div>
                <Progress value={row.online ? 100 : 0} className="h-1.5" />
              </div>
            ))}
          </div>
        </AdminPanelCard>
      </div>
    </div>
  )
}
