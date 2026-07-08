"use client"

import Link from "next/link"
import { getGradeDescription, GradeBadge } from "@/components/recalls/grade-badge"
import type { RecallItem } from "@/lib/mocks/recalls"
import { cn, formatRegisteredDate } from "@/lib/utils"

type Props = {
  item: RecallItem
  className?: string
}

export function RecallCard({ item, className }: Props) {
  return (
    <Link
      href={`/recalls/${item.id}`}
      className={cn(
        "block rounded-2xl border border-border/70 bg-card/60 p-4 text-left shadow-sm transition-colors hover:border-primary/50 hover:bg-card/80",
        className,
      )}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div className="flex min-w-0 flex-wrap items-center gap-2">
          <GradeBadge grade={item.recall_grade} />
          <h3 className="min-w-0 flex-1 truncate font-medium text-foreground">{item.product_name}</h3>
        </div>
        <span className="shrink-0 text-xs text-muted-foreground">{formatRegisteredDate(item.registered_at)}</span>
      </div>
      <p className="mt-2 text-xs text-muted-foreground">
        {item.food_type} · {item.manufacturer}
      </p>
      <p className="mt-2 line-clamp-1 text-sm text-foreground/90" title={item.recall_reason}>
        {item.recall_reason}
      </p>
      <p className="mt-1 text-[11px] text-muted-foreground">{getGradeDescription(item.recall_grade)}</p>
    </Link>
  )
}
