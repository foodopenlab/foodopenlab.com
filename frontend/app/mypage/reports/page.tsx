"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useMyPageAuth } from "@/hooks/use-mypage-auth"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import { FileText, Save, MessageSquare, ExternalLink, Calendar } from "lucide-react"
import { FeedbackModal } from "@/components/mypage/feedback-modal"
import { cn } from "@/lib/utils"

interface ReportItem {
  title: string
  url: string
  source: string
  published_at: string
}

interface ReportSection {
  type: string
  items: ReportItem[]
  is_empty: boolean
}

interface DailyReport {
  id: string
  expert_user_id: string
  report_date: string
  generated_at: string
  expires_at: string
  is_saved: boolean
  summary: string
  summary_preview: string
  sections: ReportSection[]
}

interface Category {
  code: string
  type: "media" | "foodtype"
  name_ko: string
}

export default function ReportsListPage() {
  const { token, role, isLoading: isAuthLoading } = useMyPageAuth()
  const [reports, setReports] = useState<DailyReport[]>([])
  const [categories, setCategories] = useState<Record<string, Category>>({})
  const [userIndustryCodes, setUserIndustryCodes] = useState<string[]>([])
  const [feedbackStatuses, setFeedbackStatuses] = useState<Record<string, boolean>>({}) // reportId -> true if feedback submitted
  
  const [isLoading, setIsLoading] = useState(true)
  const [isSavingMap, setIsSavingMap] = useState<Record<string, boolean>>({})
  const [selectedReportId, setSelectedReportId] = useState<string | null>(null)
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    if (isAuthLoading || !token) return
    if (role !== "expert") {
      setIsLoading(false)
      return
    }

    async function loadData() {
      try {
        setIsLoading(true)
        // 1. Fetch reports
        const reportsRes = await fetch("/api/mypage/reports", {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (!reportsRes.ok) throw new Error("리포트 목록을 불러오지 못했습니다.")
        const reportsData: DailyReport[] = await reportsRes.json()
        setReports(reportsData)

        // 2. Fetch all category names mapping
        const catRes = await fetch("/api/admin/industry-categories")
        if (catRes.ok) {
          const catList: Category[] = await catRes.json()
          const catMap: Record<string, Category> = {}
          catList.forEach(c => { catMap[c.code] = c })
          setCategories(catMap)
        }

        // 3. Fetch user industry codes to show as tags
        const indRes = await fetch("/api/mypage/industry", {
          headers: { Authorization: `Bearer ${token}` }
        })
        if (indRes.ok) {
          const indData = await indRes.json()
          const codes = [
            ...(indData.media_codes || []),
            ...(indData.foodtype_selections || []).map((s: any) => s.code)
          ]
          setUserIndustryCodes(codes)
        }

        // 4. Fetch feedback submission statuses for visible reports
        const statuses: Record<string, boolean> = {}
        await Promise.all(
          reportsData.map(async (r) => {
            try {
              const fbRes = await fetch(`/api/mypage/reports/${r.id}/feedback`, {
                headers: { Authorization: `Bearer ${token}` }
              })
              statuses[r.id] = fbRes.status === 200
            } catch {
              statuses[r.id] = false
            }
          })
        )
        setFeedbackStatuses(statuses)

      } catch (err: any) {
        toast({
          variant: "destructive",
          title: "데이터 로드 실패",
          description: err.message || "오류가 발생했습니다.",
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadData()
  }, [token, isAuthLoading, role, toast])

  const handleSaveToggle = async (reportId: string) => {
    if (isSavingMap[reportId]) return
    setIsSavingMap(prev => ({ ...prev, [reportId]: true }))

    try {
      const res = await fetch(`/api/mypage/reports/${reportId}/save`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json"
        }
      })

      if (!res.ok) throw new Error("리포트 저장 상태 변경 실패")
      const updatedReport: DailyReport = await res.json()
      
      setReports(prev => prev.map(r => r.id === reportId ? updatedReport : r))
      toast({
        title: updatedReport.is_saved ? "리포트 저장 완료" : "리포트 저장 해제",
        description: updatedReport.is_saved 
          ? "해당 리포트는 만료일(7일) 이후에도 보관됩니다." 
          : "해당 리포트는 만료일이 지나면 자동 영구 삭제됩니다."
      })
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "저장 실패",
        description: err.message || "네트워크 오류가 발생했습니다."
      })
    } finally {
      setIsSavingMap(prev => ({ ...prev, [reportId]: false }))
    }
  }

  const openFeedback = (reportId: string) => {
    setSelectedReportId(reportId)
    setIsFeedbackOpen(true)
  }

  const handleFeedbackSubmitted = () => {
    if (selectedReportId) {
      setFeedbackStatuses(prev => ({ ...prev, [selectedReportId]: true }))
    }
  }

  if (isAuthLoading || isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <Skeleton className="h-8 w-48 mb-2" />
            <Skeleton className="h-4 w-80" />
          </div>
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map(i => (
            <Skeleton key={i} className="h-40 w-full rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  if (role !== "expert") {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-card border border-border rounded-xl text-center min-h-[400px]">
        <FileText className="h-12 w-12 text-muted-foreground/60 mb-3" />
        <h3 className="text-lg font-bold text-foreground mb-1">접근 권한 없음</h3>
        <p className="text-sm text-muted-foreground max-w-md">
          일일 리포트는 식품 전문가 회원에게만 제공되는 특별 브리핑 서비스입니다.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
        <div>
          <h1 className="text-xl font-bold text-foreground">일일 브리핑 리포트</h1>
          <p className="text-sm text-muted-foreground">
            선택한 업종과 관심 카테고리를 토대로 생성된 맞춤 리포트입니다. (최대 7일간 보관)
          </p>
        </div>
        <Link href="/mypage/industry">
          <Button variant="outline" size="sm" className="border-border hover:bg-muted text-xs">
            업종/뉴스 설정 변경
          </Button>
        </Link>
      </div>

      {reports.length === 0 ? (
        <div className="flex flex-col items-center justify-center p-12 bg-card border border-border rounded-xl text-center min-h-[300px]">
          <FileText className="h-14 w-14 text-muted-foreground/30 mb-4" />
          <h3 className="text-base font-bold text-foreground mb-1.5">생성된 리포트 없음</h3>
          <p className="text-xs text-muted-foreground max-w-sm">
            아직 생성된 일일 브리핑 리포트가 없습니다. 업종 설정 완료 후 내일 아침 10:30에 첫 리포트가 생성됩니다.
            <br />
            <span className="text-[11px] text-primary/80 mt-1 block">*(신규 가입자는 가입 당일 생성에서 제외됩니다)*</span>
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reports.map((report) => {
            const isSaved = report.is_saved
            const isSaving = isSavingMap[report.id]
            const hasFeedback = feedbackStatuses[report.id]
            const formattedDate = new Date(report.report_date).toLocaleDateString("ko-KR", {
              year: "numeric",
              month: "long",
              day: "numeric",
            })

            // Find matching category tags for this report
            const matchedTags = userIndustryCodes
              .map(code => categories[code]?.name_ko)
              .filter(Boolean)

            return (
              <div
                key={report.id}
                className="group relative flex flex-col justify-between p-5 bg-card border border-border hover:border-primary/20 rounded-xl shadow-sm transition-all duration-300 hover:shadow-md"
              >
                <div>
                  {/* Card Header */}
                  <div className="flex flex-wrap items-center justify-between gap-2.5 mb-3">
                    <div className="flex items-center gap-2 text-foreground">
                      <Calendar className="h-4 w-4 text-primary" />
                      <span className="text-sm font-bold">{formattedDate}</span>
                      {isSaved && (
                        <Badge variant="secondary" className="bg-primary/10 text-primary border-none text-[10px] font-semibold py-0.5">
                          보관됨
                        </Badge>
                      )}
                    </div>
                    {/* Tags */}
                    <div className="flex flex-wrap gap-1">
                      {matchedTags.slice(0, 3).map((tag, idx) => (
                        <Badge key={idx} variant="outline" className="text-[10px] border-border text-muted-foreground bg-muted/20">
                          {tag}
                        </Badge>
                      ))}
                      {matchedTags.length > 3 && (
                        <Badge variant="outline" className="text-[10px] border-border text-muted-foreground bg-muted/20">
                          +{matchedTags.length - 3}
                        </Badge>
                      )}
                    </div>
                  </div>

                  {/* Summary Preview */}
                  <p className="text-xs text-muted-foreground/90 line-clamp-3 leading-relaxed mb-4">
                    {report.summary_preview || "리포트 요약 내용을 불러오는 중입니다."}
                  </p>
                </div>

                {/* Actions */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-3.5 border-t border-border/60">
                  <Link href={`/mypage/reports/${report.id}`}>
                    <Button size="sm" variant="outline" className="text-xs h-8.5 font-medium border-border hover:bg-muted text-foreground">
                      상세 보기
                      <ExternalLink className="h-3.5 w-3.5 ml-1.5 opacity-80" />
                    </Button>
                  </Link>

                  <div className="flex items-center gap-2">
                    {/* Save Button */}
                    <Button
                      size="sm"
                      variant={isSaved ? "default" : "outline"}
                      onClick={() => handleSaveToggle(report.id)}
                      disabled={isSaving}
                      className={cn(
                        "text-xs h-8.5 px-3.5 font-medium transition-all duration-200",
                        isSaved 
                          ? "bg-primary text-primary-foreground hover:bg-primary/95" 
                          : "border-border hover:bg-muted text-muted-foreground hover:text-foreground"
                      )}
                    >
                      {isSaving ? (
                        <Spinner className="h-3.5 w-3.5 mr-1.5" />
                      ) : (
                        <Save className="h-3.5 w-3.5 mr-1.5" />
                      )}
                      {isSaved ? "보관 취소" : "보관"}
                    </Button>

                    {/* Feedback Button */}
                    {!hasFeedback ? (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => openFeedback(report.id)}
                        className="text-xs h-8.5 px-3.5 font-medium border-primary/25 hover:border-primary/45 bg-primary/5 hover:bg-primary/10 text-primary"
                      >
                        <MessageSquare className="h-3.5 w-3.5 mr-1.5" />
                        피드백 작성
                      </Button>
                    ) : (
                      <Badge variant="outline" className="text-xs h-8.5 px-3 font-medium border-muted/80 text-muted-foreground bg-muted/10 flex items-center gap-1 cursor-default select-none">
                        피드백 완료
                      </Badge>
                    )}
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}

      {/* Feedback Modal */}
      {selectedReportId && (
        <FeedbackModal
          isOpen={isFeedbackOpen}
          onClose={() => {
            setIsFeedbackOpen(false)
            setSelectedReportId(null)
          }}
          reportId={selectedReportId}
          token={token!}
          onFeedbackSubmitted={handleFeedbackSubmitted}
        />
      )}
    </div>
  )
}
