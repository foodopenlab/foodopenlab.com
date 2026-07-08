"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { 
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer 
} from "recharts"
import { 
  Brain, Save, ShieldAlert, Ban, UserCheck, RefreshCw, Landmark, Coins, HelpCircle, CheckCircle2, AlertCircle 
} from "lucide-react"

type CostItem = {
  date: string
  request_count: number
  input_tokens: number
  output_tokens: number
  estimated_cost_usd: number
  estimated_cost_krw: number
  is_mocked: boolean
}

type CostData = {
  daily: CostItem[]
  total_requests: number
  total_input_tokens: number
  total_output_tokens: number
  total_cost_usd: number
  total_cost_krw: number
}

type PromptData = {
  prompt_analysis: string
  prompt_regulation: string
  blocked_users: string[]
}

export default function AdminAiSettingsPage() {
  const [activeTab, setActiveTab] = useState("prompts")
  const [prompts, setPrompts] = useState<PromptData | null>(null)
  const [costs, setCosts] = useState<CostData | null>(null)
  const [loading, setLoading] = useState(true)
  const [savingPrompt, setSavingPrompt] = useState(false)
  const [blockingUser, setBlockingUser] = useState(false)
  const [newBlockId, setNewBlockId] = useState("")
  
  const [mounted, setMounted] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  useEffect(() => {
    setMounted(true)
  }, [])

  const loadPrompts = useCallback(async () => {
    try {
      const res = await adminFetch("/admin/ai-settings/prompt")
      if (!res.ok) throw new Error("프롬프트 설정을 가져오는데 실패했습니다.")
      const data = (await res.json()) as PromptData
      setPrompts(data)
    } catch (err: any) {
      setError(err.message || "로딩 오류")
    }
  }, [])

  const loadCosts = useCallback(async () => {
    try {
      const res = await adminFetch("/admin/ai-settings/costs")
      if (!res.ok) throw new Error("비용 통계를 가져오는데 실패했습니다.")
      const data = (await res.json()) as CostData
      setCosts(data)
    } catch (err: any) {
      setError(err.message || "로딩 오류")
    }
  }, [])

  const loadAll = useCallback(async () => {
    setLoading(true)
    setError(null)
    setSuccess(null)
    await Promise.all([loadPrompts(), loadCosts()])
    setLoading(false)
  }, [loadPrompts, loadCosts])

  useEffect(() => {
    void loadAll()
  }, [loadAll])

  const savePrompts = async () => {
    if (!prompts) return
    setSavingPrompt(true)
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch("/admin/ai-settings/prompt", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt_analysis: prompts.prompt_analysis,
          prompt_regulation: prompts.prompt_regulation,
        }),
      })
      if (!res.ok) throw new Error("프롬프트 저장 실패")
      setSuccess("AI 프롬프트 설정이 실시간으로 동기화되어 반영되었습니다.")
    } catch (err: any) {
      setError(err.message || "저장 실패")
    } finally {
      setSavingPrompt(false)
    }
  }

  const blockUser = async () => {
    const id = newBlockId.trim()
    if (!id || !prompts) return
    setBlockingUser(true)
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch("/admin/ai-settings/block-user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: id }),
      })
      if (!res.ok) throw new Error("사용자 차단 실패")
      const data = await res.json()
      setPrompts({ ...prompts, blocked_users: data.blocked_users })
      setNewBlockId("")
      setSuccess(`사용자 ID '${id}'의 AI 서비스 사용이 정상적으로 차단되었습니다.`)
    } catch (err: any) {
      setError(err.message || "차단 실패")
    } finally {
      setBlockingUser(false)
    }
  }

  const unblockUser = async (id: string) => {
    if (!prompts) return
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch("/admin/ai-settings/unblock-user", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id: id }),
      })
      if (!res.ok) throw new Error("차단 해제 실패")
      const data = await res.json()
      setPrompts({ ...prompts, blocked_users: data.blocked_users })
      setSuccess(`사용자 ID '${id}'의 AI 서비스 이용 제한이 정상 해제되었습니다.`)
    } catch (err: any) {
      setError(err.message || "해제 실패")
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <Brain className="text-primary size-7" />
            AI 설정 및 비용 센터
          </h1>
          <p className="text-sm text-muted-foreground">
            Gemini AI의 시스템 프롬프트를 튜닝하고 API 호출 비용 추이 관리 및 비정상 사용자를 관리합니다.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => void loadAll()}
          disabled={loading}
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

      {success && (
        <div className="flex items-center gap-3 rounded-lg border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-500">
          <CheckCircle2 className="size-5 shrink-0" />
          <div>{success}</div>
        </div>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="bg-muted/50 p-1 border border-border/50 rounded-lg">
          <TabsTrigger value="prompts" className="rounded-md font-medium">🤖 AI 프롬프트 튜닝</TabsTrigger>
          <TabsTrigger value="costs" className="rounded-md font-medium">📊 토큰 및 비용 통계</TabsTrigger>
          <TabsTrigger value="blocks" className="rounded-md font-medium">🚫 악성 유저 차단 센터</TabsTrigger>
        </TabsList>

        {/* AI Prompts Tab */}
        <TabsContent value="prompts" className="space-y-6">
          {loading || !prompts ? (
            <div className="space-y-6">
              <Skeleton className="h-64 w-full rounded-xl" />
              <Skeleton className="h-64 w-full rounded-xl" />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="rounded bg-primary/10 px-2.5 py-1 text-xs font-semibold text-primary">원료분석 챗봇</span>
                  <h3 className="text-base font-semibold">AI 원료 위해·규격 분석 프롬프트 (prompt_analysis)</h3>
                </div>
                <p className="text-xs text-muted-foreground mb-4">
                  원재료 위해성 가독성 정보 제공 및 식품안전나라 교차 검증 하이퍼링크 기본 도메인 안내 정책을 수립합니다.
                </p>
                <Textarea
                  value={prompts.prompt_analysis}
                  onChange={(e) => setPrompts({ ...prompts, prompt_analysis: e.target.value })}
                  className="min-h-[160px] font-mono text-sm leading-relaxed"
                />
              </div>

              <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="rounded bg-amber-500/10 px-2.5 py-1 text-xs font-semibold text-amber-500">법규 챗봇</span>
                  <h3 className="text-base font-semibold">식품법규 전문 어시스턴트 프롬프트 (prompt_regulation)</h3>
                </div>
                <p className="text-xs text-muted-foreground mb-4">
                  법제처 국가법령정보센터 조문 기반 매핑 및 검색 경로 안내, 회사 업종 변수 처리가 포함된 템플릿입니다. 
                  <span className="text-destructive font-semibold"> 주의: {"{req.company_type}"} 및 {"{retrieved_articles}"} 플레이스홀더를 반드시 유지해주세요.</span>
                </p>
                <Textarea
                  value={prompts.prompt_regulation}
                  onChange={(e) => setPrompts({ ...prompts, prompt_regulation: e.target.value })}
                  className="min-h-[220px] font-mono text-sm leading-relaxed"
                />
              </div>

              <div className="flex justify-end">
                <Button onClick={() => void savePrompts()} disabled={savingPrompt} className="gap-2 px-6 shadow-sm">
                  <Save className="size-4" />
                  {savingPrompt ? "적용 저장 중..." : "AI 프롬프트 즉시 반영 저장"}
                </Button>
              </div>
            </div>
          )}
        </TabsContent>

        {/* Token & Costs Tab */}
        <TabsContent value="costs" className="space-y-6">
          {loading || !costs ? (
            <div className="space-y-6">
              <div className="grid gap-4 md:grid-cols-4">
                {[0, 1, 2, 3].map((i) => <Skeleton key={i} className="h-28 rounded-xl" />)}
              </div>
              <Skeleton className="h-96 w-full rounded-xl" />
            </div>
          ) : (
            <div className="space-y-6">
              {/* Cost Summary Cards */}
              <div className="grid gap-4 sm:grid-cols-2 md:grid-cols-4">
                <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                  <p className="text-xs font-medium text-muted-foreground">총 호출 횟수 (15일 누적)</p>
                  <p className="mt-2 text-2xl font-bold">{costs.total_requests.toLocaleString()} <span className="text-sm font-normal text-muted-foreground">회</span></p>
                  <div className="mt-1 flex items-center gap-1 text-[10px] text-primary">
                    <RefreshCw className="size-3 shrink-0" />
                    <span>Gemini 1.5 Flash 연동</span>
                  </div>
                </div>

                <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                  <p className="text-xs font-medium text-muted-foreground">총 사용 토큰 (소비량)</p>
                  <p className="mt-2 text-xl font-bold">{(costs.total_input_tokens + costs.total_output_tokens).toLocaleString()} <span className="text-sm font-normal text-muted-foreground">Tokens</span></p>
                  <p className="text-[10px] text-muted-foreground mt-1 truncate">
                    Input: {costs.total_input_tokens.toLocaleString()} / Output: {costs.total_output_tokens.toLocaleString()}
                  </p>
                </div>

                <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                  <p className="text-xs font-medium text-muted-foreground">누적 예측 비용 (USD)</p>
                  <p className="mt-2 text-2xl font-bold flex items-center gap-1.5 text-primary">
                    <Landmark className="size-5 text-primary/80" />
                    ${costs.total_cost_usd.toFixed(4)}
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    Input $0.075/1M, Output $0.30/1M 기준
                  </p>
                </div>

                <div className="rounded-xl border border-border bg-card p-4 shadow-sm">
                  <p className="text-xs font-medium text-muted-foreground">누적 비용 환산 (KRW)</p>
                  <p className="mt-2 text-2xl font-bold flex items-center gap-1.5 text-emerald-500">
                    <Coins className="size-5 text-emerald-500/80" />
                    {costs.total_cost_krw.toLocaleString()} 원
                  </p>
                  <p className="text-[10px] text-muted-foreground mt-1">
                    한화 환율 고정 기준 (1,380원 환산)
                  </p>
                </div>
              </div>

              {/* Recharts Chart */}
              <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
                <h3 className="text-base font-semibold mb-6">최근 15일 일일 호출 건수 및 소요 비용 추이</h3>
                <div className="h-96 w-full">
                  {mounted && costs.daily.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={costs.daily} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
                        <XAxis 
                          dataKey="date" 
                          tickFormatter={(d) => d.slice(5)} 
                          stroke="rgba(255,255,255,0.4)" 
                          fontSize={11} 
                        />
                        <YAxis 
                          yAxisId="left" 
                          orientation="left" 
                          stroke="rgba(255,255,255,0.4)" 
                          fontSize={11}
                          label={{ value: '호출 횟수', angle: -90, position: 'insideLeft', offset: 10, style: { fill: 'rgba(255,255,255,0.4)', fontSize: 11 } }}
                        />
                        <YAxis 
                          yAxisId="right" 
                          orientation="right" 
                          stroke="#10b981" 
                          fontSize={11}
                          label={{ value: '비용 (KRW)', angle: 90, position: 'insideRight', offset: 10, style: { fill: '#10b981', fontSize: 11 } }}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#1e1e2e", borderColor: "rgba(255,255,255,0.1)", borderRadius: "8px" }} 
                          labelStyle={{ color: "#fff", fontWeight: "bold" }}
                        />
                        <Legend wrapperStyle={{ fontSize: "12px", marginTop: "10px" }} />
                        <Bar yAxisId="left" dataKey="request_count" name="호출 수 (회)" fill="#7c3aed" radius={[4, 4, 0, 0]} />
                        <Line yAxisId="right" type="monotone" dataKey="estimated_cost_krw" name="예측비용 (원)" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} />
                      </BarChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                      차트를 표시할 수 없습니다.
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </TabsContent>

        {/* User Block Manager Tab */}
        <TabsContent value="blocks" className="space-y-6">
          {loading || !prompts ? (
            <div className="space-y-6">
              <Skeleton className="h-28 w-full rounded-xl" />
              <Skeleton className="h-64 w-full rounded-xl" />
            </div>
          ) : (
            <div className="space-y-6">
              <div className="rounded-xl border border-border bg-card p-6 shadow-sm">
                <h3 className="text-base font-semibold mb-2">악성 AI 챗봇 이용자 제재 관리</h3>
                <p className="text-xs text-muted-foreground mb-6">
                  Gemini API 할당량을 비정상적으로 소모하거나 무차별적인 법적 다툼용 데이터를 반복 요청하는 사용자의 AI 사용을 제한합니다.
                  차단된 사용자는 원료분석 챗봇 및 법규 챗봇에 접속하더라도 AI 호출 대신 서비스 일시 제한 안내를 받게 됩니다.
                </p>

                <div className="flex gap-3 max-w-md">
                  <Input
                    placeholder="차단할 사용자 고유 ID 입력 (예: 42)"
                    value={newBlockId}
                    onChange={(e) => setNewBlockId(e.target.value)}
                    className="font-semibold"
                  />
                  <Button onClick={() => void blockUser()} disabled={blockingUser} className="gap-2 shadow-sm font-semibold">
                    <Ban className="size-4" />
                    즉시 차단 등록
                  </Button>
                </div>
              </div>

              {/* Blocked Users Table */}
              <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
                <div className="p-4 border-b border-border bg-muted/20">
                  <h4 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                    <ShieldAlert className="size-4 text-destructive" />
                    제한 설정된 사용자 계정 리스트 ({prompts.blocked_users.length} 명)
                  </h4>
                </div>
                
                {prompts.blocked_users.length === 0 ? (
                  <div className="p-8 text-center text-sm text-muted-foreground">
                    현재 AI 이용이 일시 제한된 사용자가 없습니다.
                  </div>
                ) : (
                  <table className="w-full text-left border-collapse text-sm">
                    <thead>
                      <tr className="border-b border-border/80 text-muted-foreground bg-muted/10">
                        <th className="p-3.5 font-medium">제한 사용자 고유 ID (User ID)</th>
                        <th className="p-3.5 font-medium">서비스 차단 항목</th>
                        <th className="p-3.5 font-medium">현재 작동 상태</th>
                        <th className="p-3.5 font-medium text-right">관리 작업</th>
                      </tr>
                    </thead>
                    <tbody>
                      {prompts.blocked_users.map((id) => (
                        <tr key={id} className="border-b border-border/50 hover:bg-muted/10 transition-colors">
                          <td className="p-3.5 font-mono font-semibold text-foreground">{id}</td>
                          <td className="p-3.5">
                            <span className="rounded bg-destructive/10 px-2 py-0.5 text-[11px] font-medium text-destructive">
                              원재료분석 / 법규 전체 차단
                            </span>
                          </td>
                          <td className="p-3.5">
                            <span className="flex items-center gap-1 text-xs text-rose-500 font-medium">
                              <Ban className="size-3.5" />
                              이용 전면 제한 중
                            </span>
                          </td>
                          <td className="p-3.5 text-right">
                            <Button
                              variant="outline"
                              size="sm"
                              className="border-emerald-500/30 text-emerald-500 hover:bg-emerald-500/10 gap-1 font-semibold text-xs py-1"
                              onClick={() => void unblockUser(id)}
                            >
                              <UserCheck className="size-3.5" />
                              차단 해제 (이용 허가)
                            </Button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
              </div>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  )
}
