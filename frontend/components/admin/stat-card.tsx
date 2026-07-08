"use client"

import type { LucideIcon } from "lucide-react"
import { cn } from "@/lib/utils"

type StatCardProps = {
  title: string
  icon: LucideIcon
  children: React.ReactNode
  className?: string
}

export function StatCard({ title, icon: Icon, children, className }: StatCardProps) {
  return (
    <div
      className={cn(
        "rounded-lg border border-border bg-card p-5 text-card-foreground shadow-sm",
        className,
      )}
    >
      <div className="mb-3 flex items-center gap-2 text-muted-foreground">
        <Icon className="size-5 shrink-0 text-primary" aria-hidden />
        <span className="text-sm font-medium">{title}</span>
      </div>
      <div className="space-y-1 text-sm">{children}</div>
    </div>
  )
}
