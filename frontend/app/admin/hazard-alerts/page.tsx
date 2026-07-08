"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { Checkbox } from "@/components/ui/checkbox"
import { 
  AlertTriangle, Send, Bell, Mail, MessageCircle, RefreshCw, AlertCircle, CheckCircle2, Search, ArrowRight 
} from "lucide-react"

type MatchedCompany = {
  name: string
  business_no: string
  type: string
  representative: string
  email: string
  phone: string
}

type HazardAlert = {
  id: string
  product_name: string
  manufacturer: string
  food_type: string
  reason: string
  registered_at: string
  hazard_level: string
  matched_companies: MatchedCompany[]
}

type DispatchLog = {
  company_name: string
  channel: string
  destination: string
  status: "success" | "failed"
  dispatched_at: string
  error: string | null
}

export default function AdminHazardAlertsPage() {
  const [alerts, setAlerts] = useState<HazardAlert[]>([])
  const [selectedAlert, setSelectedAlert] = useState<HazardAlert | null>(null)
  const [loading, setLoading] = useState(true)
  const [dispatching, setDispatching] = useState(false)
  const [channels, setChannels] = useState<string[]>(["email", "kakao"])
  
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [logs, setLogs] = useState<DispatchLog[]>([])

  const loadAlerts = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminFetch("/admin/hazard-alerts/latest")
      if (!res.ok) throw new Error("최근 위해 정보를 가져오는데 실패했습니다.")
      const data = (await res.json()) as HazardAlert[]
      setAlerts(data)
      if (data.length > 0 && !selectedAlert) {
        setSelectedAlert(data[0])
      }
    } catch (err: any) {
      setError(err.message || "로딩 오류")
    } finally {
      setLoading(false)
    }
  }, [selectedAlert])

  useEffect(() => {
    void loadAlerts()
  }, [loadAlerts])

  const toggleChannel = (channel: string) => {
    if (channels.includes(channel)) {
      setChannels(channels.filter((c) => c !== channel))
    } else {
      setChannels([...channels, channel])
    }
  }

  const dispatchAlert = async () => {
    if (!selectedAlert || channels.length === 0) return
    setDispatching(true)
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch("/admin/hazard-alerts/dispatch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          alert_id: selectedAlert.id,
          product_name: selectedAlert.product_name,
          reason: selectedAlert.reason,
          channels: channels,
          target_companies: selectedAlert.matched_companies,
        }),
      })
      if (!res.ok) throw new Error("긴급 위해 경보 발송 실패")
      const data = await res.json()
      setLogs(data.logs || [])
      setSuccess(
        `긴급 위해 경보가 ${selectedAlert.matched_companies.length}개 연동 업체에 다중 채널을 통해 성공적으로 발송되었습니다.`
      )
    } catch (err: any) {
      setError(err.message || "발송 오류")
    } finally {
      setDispatching(false)
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between border-b border-border pb-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground flex items-center gap-2">
            <AlertTriangle className="text-destructive size-7 animate-pulse" />
            위해 신속 경보 발송 (Hazard Alert Dispatcher)
          </h1>
          <p className="text-sm text-muted-foreground">
            최근 탐지된 긴급 안전 회수 및 행정처분 성분을 분석하여 해당 원료를 취급/사용하는 제조사에 다중 채널(Email/Kakao/App Push)로 긴급 위해 경보를 긴급 발송합니다.
          </p>
        </div>
        <Button
          variant="outline"
          onClick={() => void loadAlerts()}
          disabled={loading || dispatching}
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

      {loading && alerts.length === 0 ? (
        <div className="grid gap-6 md:grid-cols-3">
          <Skeleton className="h-96 w-full rounded-xl md:col-span-1" />
          <Skeleton className="h-96 w-full rounded-xl md:col-span-2" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-3">
          {/* Recent Violations Feed List */}
          <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm md:col-span-1 flex flex-col max-h-[640px]">
            <div className="p-4 border-b border-border bg-muted/20">
              <h2 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                <Search className="size-4 text-primary" />
                위해 탐지 피드 ({alerts.length})
              </h2>
            </div>
            
            <div className="flex-1 overflow-y-auto divide-y divide-border/60">
              {alerts.map((a) => (
                <button
                  key={a.id}
                  onClick={() => {
                    setSelectedAlert(a)
                    setLogs([])
                    setSuccess(null)
                  }}
                  className={`w-full text-left p-4 transition-all hover:bg-muted/10 flex flex-col gap-1.5 ${
                    selectedAlert?.id === a.id ? "bg-primary/5 border-l-4 border-primary font-medium" : ""
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-xs text-muted-foreground whitespace-nowrap">{a.registered_at}</span>
                    <span className={`text-[10px] px-1.5 py-0.5 rounded font-semibold ${
                      a.hazard_level === "고" ? "bg-rose-500/15 text-rose-500" : "bg-amber-500/15 text-amber-500"
                    }`}>
                      {a.hazard_level === "고" ? "긴급위해" : "주의원료"}
                    </span>
                  </div>
                  <h3 className="text-sm font-bold text-foreground truncate">{a.product_name}</h3>
                  <p className="text-xs text-muted-foreground truncate">{a.reason}</p>
                  <p className="text-[11px] text-muted-foreground">유형: {a.food_type}</p>
                </button>
              ))}
            </div>
          </div>

          {/* Alert Dispatch Console */}
          <div className="rounded-xl border border-border bg-card p-6 shadow-sm md:col-span-2 space-y-6">
            {selectedAlert ? (
              <>
                <div className="border-b border-border/80 pb-4">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="bg-destructive/15 text-destructive rounded px-2 py-0.5 text-xs font-semibold">
                      탐지 위해 정보 분석
                    </span>
                    <span className="text-xs text-muted-foreground">ID: {selectedAlert.id}</span>
                  </div>
                  <h2 className="text-xl font-bold text-foreground mb-1">{selectedAlert.product_name}</h2>
                  <p className="text-sm text-muted-foreground">
                    제조사: {selectedAlert.manufacturer} | 혐의 사유: <span className="text-rose-500 font-semibold">{selectedAlert.reason}</span>
                  </p>
                </div>

                {/* Matched Companies Section */}
                <div className="space-y-3">
                  <h3 className="text-sm font-semibold text-foreground">
                    ⚠️ 해당 성분/식품군 취급 연동 제조사 매핑 ({selectedAlert.matched_companies.length}개 업체)
                  </h3>
                  <div className="rounded-lg border border-border bg-muted/10 overflow-hidden divide-y divide-border/50 text-xs">
                    {selectedAlert.matched_companies.map((c, i) => (
                      <div key={i} className="p-3 flex items-center justify-between hover:bg-muted/10 transition-colors">
                        <div className="space-y-1">
                          <p className="font-bold text-foreground text-sm flex items-center gap-1.5">
                            {c.name}
                            <span className="rounded bg-primary/10 text-primary px-1.5 py-0.2 text-[10px] font-normal">
                              {c.type}
                            </span>
                          </p>
                          <p className="text-muted-foreground text-xs">
                            사업자 번호: {c.business_no} | 대표: {c.representative}
                          </p>
                        </div>
                        <div className="text-right text-muted-foreground text-xs space-y-0.5">
                          <p>이메일: {c.email}</p>
                          <p>연락처: {c.phone}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Multi Channel Dispatch Console */}
                <div className="rounded-xl bg-muted/20 border border-border p-4 space-y-4">
                  <h3 className="text-sm font-semibold text-foreground flex items-center gap-1.5">
                    <Send className="size-4 text-primary" />
                    다중 채널 발송 설정
                  </h3>
                  
                  <div className="flex flex-wrap gap-6">
                    <label className="flex items-center gap-2 text-xs font-semibold cursor-pointer">
                      <Checkbox
                        checked={channels.includes("email")}
                        onCheckedChange={() => toggleChannel("email")}
                      />
                      <Mail className="size-4 text-amber-500" />
                      이메일 경보 발송
                    </label>

                    <label className="flex items-center gap-2 text-xs font-semibold cursor-pointer">
                      <Checkbox
                        checked={channels.includes("kakao")}
                        onCheckedChange={() => toggleChannel("kakao")}
                      />
                      <MessageCircle className="size-4 text-yellow-500" />
                      카카오 알림톡 경보 발송
                    </label>

                    <label className="flex items-center gap-2 text-xs font-semibold cursor-pointer">
                      <Checkbox
                        checked={channels.includes("push")}
                        onCheckedChange={() => toggleChannel("push")}
                      />
                      <Bell className="size-4 text-purple-500" />
                      스마트 앱 푸시 경보 발송
                    </label>
                  </div>
                  
                  <div className="flex justify-end pt-2">
                    <Button
                      onClick={() => void dispatchAlert()}
                      disabled={dispatching || channels.length === 0}
                      className="gap-2 px-6 shadow-sm bg-destructive text-destructive-foreground hover:bg-destructive/90 font-bold"
                    >
                      <AlertTriangle className="size-4 animate-bounce" />
                      {dispatching ? "긴급 위해 특보 발송 중..." : "긴급 위해 경보 다중 특보 발송"}
                    </Button>
                  </div>
                </div>

                {/* Dispatch Logs Table */}
                {logs.length > 0 && (
                  <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
                    <div className="p-3 border-b border-border bg-muted/20">
                      <h4 className="text-xs font-bold text-foreground">
                        실시간 다중 채널 발송 결과 보고서
                      </h4>
                    </div>
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-border/80 text-muted-foreground bg-muted/10">
                          <th className="p-3 font-semibold">대상 업체명</th>
                          <th className="p-3 font-semibold">발송 채널</th>
                          <th className="p-3 font-semibold">수신처</th>
                          <th className="p-3 font-semibold">진행 상태</th>
                          <th className="p-3 font-semibold">비고 / 에러 사유</th>
                        </tr>
                      </thead>
                      <tbody>
                        {logs.map((l, i) => (
                          <tr key={i} className="border-b border-border/50 hover:bg-muted/5 transition-colors">
                            <td className="p-3 font-bold text-foreground">{l.company_name}</td>
                            <td className="p-3 capitalize font-semibold">{l.channel}</td>
                            <td className="p-3 font-mono text-muted-foreground">{l.destination}</td>
                            <td className="p-3">
                              <span className={`px-2 py-0.5 rounded font-semibold text-[10px] ${
                                l.status === "success" 
                                  ? "bg-emerald-500/15 text-emerald-500" 
                                  : "bg-destructive/15 text-destructive"
                              }`}>
                                {l.status === "success" ? "성공" : "실패"}
                              </span>
                            </td>
                            <td className="p-3 text-muted-foreground">{l.error || "정상 전송 완료"}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </>
            ) : (
              <div className="flex h-64 items-center justify-center text-sm text-muted-foreground">
                위해 탐지 피드에서 회수 정보를 선택해주세요.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
