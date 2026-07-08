import { Badge } from "@/components/ui/badge"
import type { SupplierRiskLevel } from "@/lib/types/supplier"
import { cn } from "@/lib/utils"

const META: Record<SupplierRiskLevel, { label: string; className: string }> = {
  HIGH: { label: "HIGH", className: "border-red-500/40 bg-red-500/15 text-red-300" },
  MEDIUM: { label: "MEDIUM", className: "border-orange-500/40 bg-orange-500/15 text-orange-200" },
  LOW: { label: "LOW", className: "border-yellow-500/40 bg-yellow-500/15 text-yellow-200" },
  NONE: { label: "NONE", className: "border-green-500/40 bg-green-500/15 text-green-300" },
}

export function RiskLevelBadge({ level, className }: { level: SupplierRiskLevel; className?: string }) {
  const meta = META[level]
  return (
    <Badge variant="outline" className={cn("text-sm font-semibold", meta.className, className)}>
      {meta.label}
    </Badge>
  )
}

export function riskLevelDescription(level: SupplierRiskLevel): string {
  if (level === "HIGH") return "즉시 검토·대체 납품 검토 권장"
  if (level === "MEDIUM") return "계약·입고 전 추가 확인 권장"
  if (level === "LOW") return "이력은 있으나 상대적으로 경미"
  return "캐시 기준 특이 이력 없음"
}
