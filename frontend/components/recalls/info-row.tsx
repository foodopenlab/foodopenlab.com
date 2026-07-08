import type { ReactNode } from "react"

export function InfoRow({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div className="grid gap-2 border-b border-border/60 py-3 text-sm sm:grid-cols-[7rem_1fr]">
      <dt className="text-muted-foreground">{label}</dt>
      <dd className="text-foreground">{children}</dd>
    </div>
  )
}
