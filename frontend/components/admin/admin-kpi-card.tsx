"use client"

import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

type AdminKpiCardProps = {
  title: string
  value: string
  delta?: string
  deltaTone?: "up" | "down" | "neutral"
  icon: LucideIcon
  className?: string
}

export function AdminKpiCard({
  title,
  value,
  delta,
  deltaTone = "neutral",
  icon: Icon,
  className,
}: AdminKpiCardProps) {
  return (
    <div
      className={cn(
        "relative overflow-hidden rounded-2xl border border-border/60 bg-card p-4 shadow-sm sm:p-5",
        className,
      )}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 space-y-2">
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">{value}</p>
          {delta ? (
            <p
              className={cn(
                "truncate text-xs font-medium",
                deltaTone === "up" && "text-primary",
                deltaTone === "down" && "text-amber-500",
                deltaTone === "neutral" && "text-muted-foreground",
              )}
              title={delta}
            >
              {delta}
            </p>
          ) : null}
        </div>
        <div className="flex size-12 shrink-0 items-center justify-center rounded-2xl bg-primary/10 text-primary">
          <Icon className="size-6" aria-hidden />
        </div>
      </div>
    </div>
  )
}
