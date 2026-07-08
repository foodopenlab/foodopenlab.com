import Link from "next/link"
import { ProcessBadge } from "@/components/enforcement/process-badge"
import type { EnforcementItem } from "@/lib/mocks/enforcement"
import { formatRegisteredDate } from "@/lib/utils"

export function EnforcementCard({ item }: { item: EnforcementItem }) {
  return (
    <Link
      href={`/enforcement/${item.id}`}
      className="block rounded-2xl border border-border/70 bg-card/60 p-4 text-left shadow-sm transition-colors hover:border-primary/50 hover:bg-card/80"
    >
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="min-w-0 flex flex-wrap items-center gap-2">
          <ProcessBadge processType={item.process_type} />
          <h3 className="min-w-0 truncate font-medium text-foreground">{item.business_name}</h3>
        </div>
        <span className="shrink-0 text-xs text-muted-foreground">{formatRegisteredDate(item.process_date)}</span>
      </div>
      <p className="mt-3 text-sm text-muted-foreground">
        {item.business_type} · {item.address}
      </p>
      <p className="mt-3 line-clamp-1 text-sm text-foreground/90">{item.violation_content}</p>
    </Link>
  )
}
