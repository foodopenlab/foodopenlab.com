"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useMyPageAuth } from "@/hooks/use-mypage-auth"
import { Skeleton } from "@/components/ui/skeleton"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import {
  ArrowLeft,
  Calendar,
  Download,
  FileText,
  MessageSquare,
  Save,
} from "lucide-react"
import { FeedbackModal } from "@/components/mypage/feedback-modal"
import { ReportSummaryView } from "@/components/mypage/report-summary-view"
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

export default function ReportDetailPage() {
  const params = useParams()
  const reportId = params.id as string
  const { token, role, isLoading: isAuthLoading } = useMyPageAuth()
  const [report, setReport] = useState<DailyReport | null>(null)
  const [hasFeedback, setHasFeedback] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [isSaving, setIsSaving] = useState(false)
  const [isFeedbackOpen, setIsFeedbackOpen] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    if (isAuthLoading || !token || !reportId) return
    if (role !== "expert") {
      setIsLoading(false)
      return
    }

    async function loadReport() {
      try {
        setIsLoading(true)
        const res = await fetch(`/api/mypage/reports/${reportId}`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        if (!res.ok) throw new Error("리포트를 불러오지 못했습니다.")
        const data: DailyReport = await res.json()
        setReport(data)

        const fbRes = await fetch(`/api/mypage/reports/${reportId}/feedback`, {
          headers: { Authorization: `Bearer ${token}` },
        })
        setHasFeedback(fbRes.status === 200)
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "오류가 발생했습니다."
        toast({
          variant: "destructive",
          title: "데이터 로드 실패",
          description: message,
        })
      } finally {
        setIsLoading(false)
      }
    }

    loadReport()
  }, [token, isAuthLoading, role, reportId, toast])

  const handleSaveToggle = async () => {
    if (!report || isSaving) return
    setIsSaving(true)
    try {
      const res = await fetch(`/api/mypage/reports/${report.id}/save`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      })
      if (!res.ok) throw new Error("리포트 저장 상태 변경 실패")
      const updated: DailyReport = await res.json()
      setReport(updated)
      toast({
        title: updated.is_saved ? "리포트 저장 완료" : "리포트 저장 해제",
        description: updated.is_saved
          ? "해당 리포트는 만료일(7일) 이후에도 보관됩니다."
          : "해당 리포트는 만료일이 지나면 자동 영구 삭제됩니다.",
      })
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "네트워크 오류가 발생했습니다."
      toast({
        variant: "destructive",
        title: "저장 실패",
        description: message,
      })
    } finally {
      setIsSaving(false)
    }
  }

  const handleDownload = async () => {
    if (!report || !token) return
    try {
      const res = await fetch(`/api/mypage/reports/${report.id}/download`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      if (!res.ok) throw new Error("다운로드에 실패했습니다.")
      const blob = await res.blob()
      const url = URL.createObjectURL(blob)
      const a = document.createElement("a")
      a.href = url
      a.download = `daily_report_${report.report_date}.txt`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : "다운로드 오류"
      toast({
        variant: "destructive",
        title: "다운로드 실패",
        description: message,
      })
    }
  }

  if (isAuthLoading || isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-64 w-full rounded-xl" />
      </div>
    )
  }

  if (role !== "expert") {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-card border border-border rounded-xl text-center min-h-[400px]">
        <FileText className="h-12 w-12 text-muted-foreground/60 mb-3" />
        <h3 className="text-lg font-bold text-foreground mb-1">접근 권한 없음</h3>
        <p className="text-sm text-muted-foreground">일일 리포트는 식품 전문가 회원에게만 제공됩니다.</p>
      </div>
    )
  }

  if (!report) {
    return (
      <div className="space-y-4">
        <Link href="/mypage/reports">
          <Button variant="ghost" size="sm" className="text-xs -ml-2">
            <ArrowLeft className="h-3.5 w-3.5 mr-1.5" />
            목록으로
          </Button>
        </Link>
        <div className="flex flex-col items-center justify-center p-12 bg-card border border-border rounded-xl text-center">
          <p className="text-sm text-muted-foreground">리포트를 찾을 수 없습니다.</p>
        </div>
      </div>
    )
  }

  const formattedDate = new Date(report.report_date).toLocaleDateString("ko-KR", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4">
        <Link href="/mypage/reports">
          <Button variant="ghost" size="sm" className="text-xs -ml-2 text-muted-foreground hover:text-foreground">
            <ArrowLeft className="h-3.5 w-3.5 mr-1.5" />
            목록으로
          </Button>
        </Link>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-primary" />
            <h1 className="text-xl font-bold text-foreground">{formattedDate} 브리핑</h1>
            {report.is_saved && (
              <Badge variant="secondary" className="bg-primary/10 text-primary border-none text-[10px]">
                보관됨
              </Badge>
            )}
          </div>

          <div className="flex flex-wrap items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={handleDownload}
              className="text-xs h-8.5 border-border"
            >
              <Download className="h-3.5 w-3.5 mr-1.5" />
              다운로드
            </Button>
            <Button
              size="sm"
              variant={report.is_saved ? "default" : "outline"}
              onClick={handleSaveToggle}
              disabled={isSaving}
              className={cn(
                "text-xs h-8.5 px-3.5",
                report.is_saved
                  ? "bg-primary text-primary-foreground"
                  : "border-border hover:bg-muted"
              )}
            >
              {isSaving ? <Spinner className="h-3.5 w-3.5 mr-1.5" /> : <Save className="h-3.5 w-3.5 mr-1.5" />}
              {report.is_saved ? "보관 취소" : "보관"}
            </Button>
            {!hasFeedback ? (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setIsFeedbackOpen(true)}
                className="text-xs h-8.5 border-primary/25 bg-primary/5 text-primary"
              >
                <MessageSquare className="h-3.5 w-3.5 mr-1.5" />
                피드백 작성
              </Button>
            ) : (
              <Badge variant="outline" className="text-xs h-8.5 px-3 text-muted-foreground">
                피드백 완료
              </Badge>
            )}
          </div>
        </div>
      </div>

      <div className="bg-card border border-border rounded-xl p-5 sm:p-6 shadow-sm">
        <h2 className="text-sm font-bold text-foreground mb-4">요약</h2>
        <ReportSummaryView sections={report.sections} />
      </div>

      <FeedbackModal
        isOpen={isFeedbackOpen}
        onClose={() => setIsFeedbackOpen(false)}
        reportId={report.id}
        token={token!}
        onFeedbackSubmitted={() => setHasFeedback(true)}
      />
    </div>
  )
}
