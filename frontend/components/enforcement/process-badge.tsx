import { Badge } from "@/components/ui/badge"
import type { EnforcementProcessType } from "@/lib/mocks/enforcement"
import { cn } from "@/lib/utils"

const PROCESS_CLASSES: Record<EnforcementProcessType, string> = {
  영업정지: "border-red-500/30 bg-red-500/15 text-red-300",
  영업취소: "border-purple-500/30 bg-purple-500/15 text-purple-300",
  과징금: "border-orange-500/30 bg-orange-500/15 text-orange-300",
  시정명령: "border-blue-500/30 bg-blue-500/15 text-blue-300",
  기타: "border-muted-foreground/30 bg-muted text-muted-foreground",
}

export function ProcessBadge({
  processType,
  className,
}: {
  processType: EnforcementProcessType
  className?: string
}) {
  return (
    <Badge variant="outline" className={cn("shrink-0", PROCESS_CLASSES[processType], className)}>
      {processType}
    </Badge>
  )
}
