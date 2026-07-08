"use client"

import { useCallback, useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { 
  BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, 
  Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell 
} from "recharts"
import { 
  fetchFoodStatsYearly, 
  fetchFoodStatsByAgent, 
  fetchFoodStatsByFacility 
} from "@/lib/phase3-client"
import type { 
  FoodStatsYearlyResponse, 
  FoodStatsByAgentResponse, 
  FoodStatsByFacilityResponse 
} from "@/lib/types/phase3"
import { BarChart3, PieChartIcon, Presentation, RefreshCw, ShieldAlert, TrendingUp } from "lucide-react"

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#ec4899", "#14b8a6", "#6366f1", "#a855f7", "#64748b"]

export default function FoodStatsDashboardPage() {
  const [selectedYear, setSelectedYear] = useState<string>("all")
  const [yearly, setYearly] = useState<FoodStatsYearlyResponse | null>(null)
  const [agents, setAgents] = useState<FoodStatsByAgentResponse | null>(null)
  const [facilities, setFacilities] = useState<FoodStatsByFacilityResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  const loadStats = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const yr = selectedYear === "all" ? null : selectedYear
      const [yRes, aRes, fRes] = await Promise.all([
        fetchFoodStatsYearly(),
        fetchFoodStatsByAgent(yr),
        fetchFoodStatsByFacility(yr),
      ])
      setYearly(yRes)
      setAgents(aRes)
      setFacilities(fRes)
    } catch (err: any) {
      setError("식품 위해 사고 통계 실시간 연동에 실패했습니다. API 키가 등록되지 않았거나 서버 통신 한계 상태입니다.")
    } finally {
      setLoading(false)
    }
  }, [selectedYear])

  useEffect(() => {
    void loadStats()
  }, [loadStats])

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/80 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-xs uppercase tracking-wider">
            <TrendingUp className="size-4 text-primary" />
            Statistical Risk Analysis
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            식품안전공공 식중독 위해 사고 통계
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            식약처 식중독 통계 API 실시간 데이터를 기반으로 식중독 사고 발생 건수, 주요 환자수, 원인 물질 및 시설별 점유율 현황을 Recharts 다차원 분석 대시보드로 시각화합니다.
          </p>
        </div>

        <Button
          variant="outline"
          onClick={() => void loadStats()}
          disabled={loading}
          className="gap-2 shrink-0 cursor-pointer self-start md:self-end"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} />
          데이터 갱신
        </Button>
      </header>

      {/* McKinsey Style Selector Section */}
      <section className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">세부 분석 대상 연도 선택</span>
          <div className="flex flex-wrap gap-2">
            {["all", "2024", "2023", "2022", "2021", "2020", "2019"].map((yr) => (
              <Button
                key={yr}
                type="button"
                size="sm"
                variant={selectedYear === yr ? "default" : "outline"}
                onClick={() => setSelectedYear(yr)}
                className="font-medium cursor-pointer"
              >
                {yr === "all" ? "전체 기간 통합" : `${yr}년`}
              </Button>
            ))}
          </div>
        </div>
      </section>

      {loading && (!yearly || !agents || !facilities) ? (
        <div className="grid gap-6">
          <Skeleton className="h-[380px] w-full rounded-xl" />
          <div className="grid gap-6 md:grid-cols-2">
            <Skeleton className="h-[380px] rounded-xl" />
            <Skeleton className="h-[380px] rounded-xl" />
          </div>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center p-12 border border-destructive/20 bg-destructive/10 rounded-xl text-center">
          <ShieldAlert className="size-12 text-destructive mb-3" />
          <h3 className="text-lg font-bold text-foreground mb-1">통계 API 연동 지연</h3>
          <p className="text-sm text-muted-foreground max-w-md mb-4">{error}</p>
          <Button onClick={() => void loadStats()} variant="outline" className="gap-2 font-semibold cursor-pointer">
            <RefreshCw className="size-4" /> 재시도
          </Button>
        </div>
      ) : (
        <div className="grid gap-6">
          {/* Yearly Incident Trend Chart */}
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
            <h3 className="text-lg font-bold text-foreground mb-6 flex items-center gap-2 border-b border-border pb-3">
              <Presentation className="size-5 text-primary" />
              최근 6개년 식중독 사고 건수 및 총 환자 수 추이 (연도별 발생 경향)
            </h3>
            <div className="h-96 w-full">
              {mounted && yearly && yearly.data.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={yearly.data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                    <XAxis dataKey="year" stroke="rgba(255,255,255,0.4)" fontSize={11} />
                    <YAxis 
                      yAxisId="left" 
                      orientation="left" 
                      stroke="rgba(255,255,255,0.4)" 
                      fontSize={11}
                      label={{ value: '발생 사건 (건)', angle: -90, position: 'insideLeft', offset: 10, style: { fill: 'rgba(255,255,255,0.4)', fontSize: 11 } }}
                    />
                    <YAxis 
                      yAxisId="right" 
                      orientation="right" 
                      stroke="#10b981" 
                      fontSize={11}
                      label={{ value: '발생 환자 (명)', angle: 90, position: 'insideRight', offset: 10, style: { fill: '#10b981', fontSize: 11 } }}
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: "#1e1e2e", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px" }} 
                      labelStyle={{ color: "#fff", fontWeight: "bold" }}
                    />
                    <Legend wrapperStyle={{ fontSize: "12px", marginTop: "10px" }} />
                    <Bar yAxisId="left" dataKey="total_incidents" name="식중독 발생 사건 수 (건)" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                    <Line yAxisId="right" type="monotone" dataKey="total_patients" name="식중독 총 환자 수 (명)" stroke="#10b981" strokeWidth={2.5} dot={{ r: 4 }} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                  연도별 통계 데이터를 로드하지 못했습니다.
                </div>
              )}
            </div>
          </div>

          <div className="grid gap-6 md:grid-cols-2">
            {/* Agent breakdown pie chart */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-foreground mb-4 flex items-center gap-2 border-b border-border pb-3">
                  <PieChartIcon className="size-4.5 text-primary" />
                  원인균/원인물질별 발생 사건수 비중 ({selectedYear === "all" ? "전체 기간" : `${selectedYear}년`})
                </h3>
                <div className="h-72 w-full flex items-center justify-center">
                  {mounted && agents && agents.data.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <PieChart>
                        <Pie
                          data={agents.data}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={90}
                          paddingAngle={3}
                          dataKey="incidents"
                          nameKey="agent"
                        >
                          {agents.data.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                          ))}
                        </Pie>
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#1e1e2e", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px" }}
                        />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="text-sm text-muted-foreground">원인균 데이터 없음</div>
                  )}
                </div>
              </div>
              
              {/* Custom Legend */}
              <div className="grid grid-cols-2 gap-x-4 gap-y-1.5 mt-4 pt-3 border-t border-border/50 text-[11px] text-muted-foreground">
                {agents?.data.slice(0, 6).map((item, index) => (
                  <div key={item.agent} className="flex items-center gap-2">
                    <span className="h-2.5 w-2.5 rounded-sm shrink-0" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                    <span className="truncate">{item.agent} ({item.incidents}건)</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Facility breakdown bar chart */}
            <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
              <h3 className="text-base font-bold text-foreground mb-4 flex items-center gap-2 border-b border-border pb-3">
                <BarChart3 className="size-4.5 text-primary" />
                발생 시설 대분류별 환자수 규모 ({selectedYear === "all" ? "전체 기간" : `${selectedYear}년`})
              </h3>
              <div className="h-80 w-full">
                {mounted && facilities && facilities.data.length > 0 ? (
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={facilities.data}
                      layout="vertical"
                      margin={{ top: 5, right: 10, left: -10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="rgba(255,255,255,0.05)" />
                      <XAxis type="number" stroke="rgba(255,255,255,0.4)" fontSize={10} />
                      <YAxis dataKey="facility" type="category" stroke="rgba(255,255,255,0.4)" fontSize={10} width={75} />
                      <Tooltip
                        contentStyle={{ backgroundColor: "#1e1e2e", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px" }}
                      />
                      <Bar dataKey="patients" name="환자 수 (명)" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                ) : (
                  <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                    시설별 데이터 없음
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  )
}
