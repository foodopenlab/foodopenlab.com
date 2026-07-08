"use client"

import { useState } from "react"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from "@/components/ui/dialog"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { Star } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import { cn } from "@/lib/utils"

interface FeedbackModalProps {
  isOpen: boolean
  onClose: () => void
  reportId: string
  token: string
  onFeedbackSubmitted: () => void
}

const SECTIONS = [
  { id: "NEWS", label: "업계 뉴스" },
  { id: "RECALL", label: "회수·행정처분" },
  { id: "LAW", label: "법규 변동" },
  { id: "MFDS", label: "식약처 보도자료" },
  { id: "RISK", label: "식중독 위험 현황" },
  { id: "RESEARCH", label: "최신 연구 동향" },
  { id: "STATS", label: "식품산업 통계·동향" },
]

export function FeedbackModal({ isOpen, onClose, reportId, token, onFeedbackSubmitted }: FeedbackModalProps) {
  const [score, setScore] = useState<number>(0)
  const [selectedSections, setSelectedSections] = useState<string[]>([])
  const [contentFeedback, setContentFeedback] = useState("")
  const [missingFeedback, setMissingFeedback] = useState("")
  const [improvementFeedback, setImprovementFeedback] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [hoveredScore, setHoveredScore] = useState<number>(0)
  const { toast } = useToast()

  const handleSectionToggle = (sectionId: string) => {
    setSelectedSections((prev) =>
      prev.includes(sectionId) ? prev.filter((id) => id !== sectionId) : [...prev, sectionId]
    )
  }

  const isValid =
    score > 0 &&
    (contentFeedback.trim().length > 0 ||
      missingFeedback.trim().length > 0 ||
      improvementFeedback.trim().length > 0)

  const handleSubmit = async () => {
    if (!isValid) return

    setIsLoading(true)
    try {
      const res = await fetch(`/api/mypage/reports/${reportId}/feedback`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        body: JSON.stringify({
          useful_sections: selectedSections,
          content_feedback: contentFeedback.trim() || null,
          missing_feedback: missingFeedback.trim() || null,
          improvement_feedback: improvementFeedback.trim() || null,
          usefulness_score: score,
        }),
      })

      if (!res.ok) {
        const data = await res.json().catch(() => null)
        throw new Error(data?.detail || "피드백 제출에 실패했습니다.")
      }

      toast({
        title: "피드백 제출 완료",
        description: "소중한 의견이 반영되어 다음 리포트 생성에 기여합니다.",
      })
      onFeedbackSubmitted()
      onClose()
    } catch (err: any) {
      toast({
        variant: "destructive",
        title: "피드백 제출 실패",
        description: err.message || "오류가 발생했습니다. 다시 시도해 주세요.",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-md max-h-[90vh] overflow-y-auto bg-card border border-border">
        <DialogHeader>
          <DialogTitle className="text-lg font-bold text-foreground">리포트 피드백 작성</DialogTitle>
          <DialogDescription className="text-sm text-muted-foreground">
            오늘 브리핑에 대한 유용성과 개선점을 나누어 주세요.
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-5 py-2">
          {/* Usefulness Score */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground">
              1. 오늘 브리핑은 유용했나요? <span className="text-destructive">*</span>
            </label>
            <div className="flex items-center gap-1">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  onClick={() => setScore(star)}
                  onMouseEnter={() => setHoveredScore(star)}
                  onMouseLeave={() => setHoveredScore(0)}
                  className="p-1 focus:outline-none transition-colors duration-150"
                  disabled={isLoading}
                >
                  <Star
                    className={cn(
                      "h-7 w-7 transition-all duration-150",
                      star <= (hoveredScore || score)
                        ? "fill-amber-400 text-amber-400 scale-110"
                        : "text-muted-foreground/40 hover:text-amber-400/60"
                    )}
                  />
                </button>
              ))}
              {score > 0 && (
                <span className="text-sm font-medium text-amber-500 ml-2">{score}점 / 5점</span>
              )}
            </div>
          </div>

          {/* Useful Sections */}
          <div className="space-y-2">
            <label className="text-sm font-semibold text-foreground">
              2. 어떤 섹션이 가장 유용했나요? (복수 선택)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {SECTIONS.map((sec) => {
                const checked = selectedSections.includes(sec.id)
                return (
                  <div
                    key={sec.id}
                    onClick={() => !isLoading && handleSectionToggle(sec.id)}
                    className={cn(
                      "flex items-center gap-2.5 p-2.5 border rounded-lg cursor-pointer transition-all duration-200 select-none",
                      checked
                        ? "border-primary/30 bg-primary/5 text-primary"
                        : "border-border hover:bg-muted/40 text-muted-foreground hover:text-foreground"
                    )}
                  >
                    <Checkbox
                      id={`section-${sec.id}`}
                      checked={checked}
                      onCheckedChange={() => handleSectionToggle(sec.id)}
                      disabled={isLoading}
                    />
                    <label
                      htmlFor={`section-${sec.id}`}
                      className="text-xs font-medium cursor-pointer flex-1"
                    >
                      {sec.label}
                    </label>
                  </div>
                )
              })}
            </div>
          </div>

          {/* Descriptive Feedbacks */}
          <div className="space-y-3.5 border-t border-border/60 pt-4">
            <label className="text-sm font-semibold text-foreground block">
              3. 세부 의견을 입력해 주세요 (최소 1개 항목 필수) <span className="text-destructive">*</span>
            </label>

            {/* Content Feedback */}
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-muted-foreground">내용 평가</span>
              <Textarea
                value={contentFeedback}
                onChange={(e) => setContentFeedback(e.target.value)}
                placeholder="오늘 다루어진 정보들에 대한 생각을 적어주세요. (예: 오늘 소시지 관련 회수 정보가 유익했습니다.)"
                className="text-xs border-border bg-input min-h-[70px] resize-none"
                disabled={isLoading}
              />
            </div>

            {/* Missing Feedback */}
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-muted-foreground">누락된 정보</span>
              <Textarea
                value={missingFeedback}
                onChange={(e) => setMissingFeedback(e.target.value)}
                placeholder="추가되었으면 하는 정보가 있었나요? (예: 원료 삼겹살의 글로벌 가격 동향이 누락되었어요.)"
                className="text-xs border-border bg-input min-h-[70px] resize-none"
                disabled={isLoading}
              />
            </div>

            {/* Improvement Feedback */}
            <div className="space-y-1.5">
              <span className="text-xs font-semibold text-muted-foreground">개선 요청 제안</span>
              <Textarea
                value={improvementFeedback}
                onChange={(e) => setImprovementFeedback(e.target.value)}
                placeholder="시각적 구조나 요약 방식 등에 대한 개선 요구를 남겨주세요. (예: 식약처 보도자료 요약이 더 짧으면 좋겠습니다.)"
                className="text-xs border-border bg-input min-h-[70px] resize-none"
                disabled={isLoading}
              />
            </div>
          </div>
        </div>

        <DialogFooter className="border-t border-border/60 pt-3 gap-2">
          <Button variant="outline" onClick={onClose} disabled={isLoading} className="text-xs h-9 border-border">
            닫기
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={!isValid || isLoading}
            className="text-xs h-9 bg-primary text-primary-foreground hover:bg-primary/90"
          >
            {isLoading && <Spinner className="h-3.5 w-3.5 mr-1.5" />}
            피드백 제출
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
