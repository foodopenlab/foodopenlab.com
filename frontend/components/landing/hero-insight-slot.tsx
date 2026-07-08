import type { ReactNode } from "react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"

type HeroInsightSlotProps = {
  title: string
  sourceLabel?: string
  className?: string
  placeholder?: boolean
  children?: ReactNode
}

/** 히어로 우측 — API 연동 데이터 카드 (회수·판매중지와 동일 톤) */
export function HeroInsightSlot({
  title,
  sourceLabel,
  className,
  placeholder = false,
  children,
}: HeroInsightSlotProps) {
  return (
    <div
      className={cn(
        "w-full rounded-2xl border bg-card/60 p-4 text-left backdrop-blur-sm",
        placeholder ? "border-dashed border-border/60 shadow-none" : "border-border/80 shadow-sm",
        className,
      )}
    >
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <h3 className="text-sm font-semibold text-foreground">{title}</h3>
        {sourceLabel ? (
          <Badge variant="secondary" className="text-[10px] md:text-xs">
            {sourceLabel}
          </Badge>
        ) : null}
      </div>
      {children ?? (
        <p className="py-6 text-center text-xs text-muted-foreground">데이터 연동 준비 중입니다.</p>
      )}
    </div>
  )
}
