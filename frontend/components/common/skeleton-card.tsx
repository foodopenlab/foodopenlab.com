import { Skeleton } from "@/components/ui/skeleton"
import { cn } from "@/lib/utils"

export function SkeletonCard({ className }: { className?: string }) {
  return (
    <div className={cn("rounded-2xl border border-border/70 bg-card/60 p-4", className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="space-y-2">
          <Skeleton className="h-4 w-20" />
          <Skeleton className="h-5 w-56" />
        </div>
        <Skeleton className="h-4 w-20" />
      </div>
      <Skeleton className="mt-4 h-4 w-72 max-w-full" />
      <Skeleton className="mt-3 h-4 w-full" />
    </div>
  )
}
