import { Badge } from "@/components/ui/badge"
import type { RecallGrade } from "@/lib/mocks/recalls"
import { cn } from "@/lib/utils"

const GRADE_META: Record<RecallGrade, { label: string; className: string }> = {
  1: { label: "위험", className: "border-red-500/30 bg-red-500/15 text-red-300" },
  2: { label: "주의", className: "border-orange-500/30 bg-orange-500/15 text-orange-300" },
  3: { label: "경고", className: "border-yellow-500/30 bg-yellow-500/15 text-yellow-200" },
}

export function GradeBadge({ grade, className }: { grade: RecallGrade; className?: string }) {
  const meta = GRADE_META[grade]

  return (
    <Badge variant="outline" className={cn("shrink-0", meta.className, className)}>
      {grade}등급 · {meta.label}
    </Badge>
  )
}

export function getGradeDescription(grade: RecallGrade) {
  if (grade === 1) return "인체에 직접적 위해 가능성 높음"
  if (grade === 2) return "인체에 위해 가능성 있음"
  return "인체에 위해 가능성 낮음"
}
