"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import Link from "next/link"
import {
  Activity,
  MessageSquare,
  Users,
} from "lucide-react"
import {
  Area,
  AreaChart,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { adminFetch } from "@/lib/admin/auth"
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

type Dashboard = {
  users: { total: number; active: number }
  chats: {
    today_total: number
    analysis_total?: number
    ingredient_total?: number
    regulation_total: number
  }
  api: { today_calls: number; today_errors: number; top_api: string }
}

type StatItem = {
  api_name: string
  total_calls: number
  error_rate: number
  cache_hit_rate: number
}

const CHART_COLORS = ["oklch(0.72 0.17 160)", "oklch(0.828 0.189 84.429)", "oklch(0.398 0.07 227.392)"]

export default function AdminDashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null)
  const [apiStats, setApiStats] = useState<StatItem[]>([])
  const [err, setErr] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  const load = useCallback(async () => {
    setErr(null)
    setLoading(true)
    try {
      const [dashRes, statsRes] = await Promise.all([
        adminFetch("/admin/dashboard"),
        adminFetch("/admin/api-stats?period=today"),
      ])
      if (!dashRes.ok) throw new Error("load failed")
      setData((await dashRes.json()) as Dashboard)
      if (statsRes.ok) {
        const j = (await statsRes.json()) as { stats: StatItem[] }
        setApiStats(j.stats ?? [])
      } else {
        setApiStats([])
      }
    } catch {
      setErr("데이터를 불러올 수 없습니다.")
      setData(null)
      setApiStats([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void load()
  }, [load])

  const chatDonut = useMemo(() => {
    if (!data) return []
    const analysis = data.chats.analysis_total ?? data.chats.ingredient_total ?? 0
    const regulation = data.chats.regulation_total || 0
    const other = Math.max(data.chats.today_total - analysis - regulation, 0)
    return [
      { name: "원료 분석", value: analysis },
      { name: "법규 채팅", value: regulation },
      { name: "기타", value: other },
    ].filter((row) => row.value > 0)
  }, [data])

  const apiChart = useMemo(
    () =>
      apiStats.slice(0, 6).map((row) => ({
        name: row.api_name,
        calls: row.total_calls,
      })),
    [apiStats],
  )

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((i) => (
            <Skeleton key={i} className="h-32 rounded-2xl" />
          ))}
        </div>
        <div className="grid gap-4 lg:grid-cols-3">
          <Skeleton className="h-64 rounded-2xl sm:h-80 lg:col-span-2" />
          <Skeleton className="h-64 rounded-2xl sm:h-80" />
        </div>
      </div>
    )
  }

  if (err || !data) {
    return (
      <div className="flex flex-col items-center gap-4 py-16 text-center">
        <p className="text-muted-foreground">{err ?? "데이터를 불러올 수 없습니다."}</p>
        <Button type="button" variant="outline" onClick={() => void load()}>
          재시도
        </Button>
      </div>
    )
  }

  const { users, chats, api } = data
  const errorRate = api.today_calls > 0 ? (api.today_errors / api.today_calls) * 100 : 0
  const activeRate = users.total > 0 ? (users.active / users.total) * 100 : 0

  const quickLinks = [
    { href: "/admin/logs", label: "통합 로그 모니터링", status: "사용 중" },
    { href: "/admin/whitelist", label: "전문가 화이트리스트", status: "사용 중" },
    { href: "/admin/api-stats", label: "상세 API 통계", status: "사용 중" },
    { href: "/admin/siliconvalley", label: "실리콘밸리 대시보드", status: "신규" },
  ]

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        <AdminKpiCard
          title="전체 회원"
          value={String(users.total)}
          delta={`활성 ${users.active}명 · ${activeRate.toFixed(0)}%`}
          deltaTone="up"
          icon={Users}
        />
        <AdminKpiCard
          title="오늘 채팅"
          value={String(chats.today_total)}
          delta="오늘 전체 대화"
          deltaTone="neutral"
          icon={MessageSquare}
        />
        <AdminKpiCard
          title="API 호출"
          value={String(api.today_calls)}
          delta={`최다: ${api.top_api || "—"}`}
          deltaTone="up"
          icon={Activity}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <AdminPanelCard
          title="API 호출 추이"
          subtitle="오늘 서비스별 API 호출량"
          className="lg:col-span-2"
        >
          <div className="h-56 sm:h-72">
            {apiChart.length === 0 ? (
              <p className="py-16 text-center text-sm text-muted-foreground">API 통계가 없습니다.</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={apiChart} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="adminApiFill" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="oklch(0.72 0.17 160)" stopOpacity={0.35} />
                      <stop offset="95%" stopColor="oklch(0.72 0.17 160)" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} stroke="oklch(0.65 0 0)" />
                  <YAxis tick={{ fontSize: 11 }} stroke="oklch(0.65 0 0)" />
                  <Tooltip
                    contentStyle={{
                      background: "oklch(0.16 0.02 250)",
                      border: "1px solid oklch(0.28 0.02 250)",
                      borderRadius: 12,
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="calls"
                    stroke="oklch(0.72 0.17 160)"
                    fill="url(#adminApiFill)"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            )}
          </div>
        </AdminPanelCard>

        <AdminPanelCard title="채팅 분포" subtitle="오늘 대화 유형">
          <div className="h-56">
            {chatDonut.length === 0 ? (
              <p className="py-12 text-center text-sm text-muted-foreground">대화 데이터 없음</p>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={chatDonut} dataKey="value" innerRadius={55} outerRadius={85} paddingAngle={3}>
                    {chatDonut.map((_, index) => (
                      <Cell key={index} fill={CHART_COLORS[index % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
          <div className="mt-2 space-y-1 text-xs text-muted-foreground">
            {chatDonut.map((row, index) => (
              <div key={row.name} className="flex justify-between">
                <span className="flex items-center gap-2">
                  <span
                    className="inline-block size-2 rounded-full"
                    style={{ background: CHART_COLORS[index % CHART_COLORS.length] }}
                  />
                  {row.name}
                </span>
                <span>{row.value}</span>
              </div>
            ))}
          </div>
        </AdminPanelCard>
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <AdminPanelCard title="바로가기" subtitle="주요 관리 메뉴" className="lg:col-span-2">
          <div className="overflow-x-auto -mx-1 px-1">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>메뉴</TableHead>
                <TableHead>상태</TableHead>
                <TableHead className="text-right">이동</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {quickLinks.map((row) => (
                <TableRow key={row.href}>
                  <TableCell className="font-medium">{row.label}</TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "text-xs font-medium",
                        row.status === "신규" ? "text-primary" : "text-emerald-500",
                      )}
                    >
                      {row.status}
                    </span>
                  </TableCell>
                  <TableCell className="text-right">
                    <Link href={row.href} className="text-sm text-primary hover:underline">
                      열기 →
                    </Link>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          </div>
        </AdminPanelCard>

        <AdminPanelCard title="시스템 상태" subtitle="운영 지표">
          <div className="space-y-4">
            <div className="rounded-xl bg-primary/10 p-4">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-foreground">API 상태</span>
                <span className="text-primary">에러 {errorRate.toFixed(1)}%</span>
              </div>
              <Progress value={Math.max(100 - errorRate, 0)} className="h-2" />
            </div>
            <div>
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="text-muted-foreground">활성 사용자 비율</span>
                <span>{activeRate.toFixed(0)}%</span>
              </div>
              <Progress value={activeRate} className="h-2" />
            </div>
          </div>
        </AdminPanelCard>
      </div>
    </div>
  )
}
