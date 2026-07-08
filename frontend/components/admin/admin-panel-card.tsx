"use client"

import { cn } from "@/lib/utils"

type AdminPanelCardProps = {
  title: string
  subtitle?: string
  action?: React.ReactNode
  children: React.ReactNode
  className?: string
}

export function AdminPanelCard({ title, subtitle, action, children, className }: AdminPanelCardProps) {
  return (
    <section
      className={cn(
        "rounded-2xl border border-border/60 bg-card p-4 shadow-sm sm:p-5",
        className,
      )}
    >
      <div className="mb-4 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <h2 className="text-base font-semibold text-foreground">{title}</h2>
          {subtitle ? <p className="mt-0.5 text-xs text-muted-foreground">{subtitle}</p> : null}
        </div>
        {action ? <div className="shrink-0 self-start">{action}</div> : null}
      </div>
      {children}
    </section>
  )
}
