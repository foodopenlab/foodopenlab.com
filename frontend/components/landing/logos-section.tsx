import { Badge } from "@/components/ui/badge"
import { Database, ClipboardCheck } from "lucide-react"

export function LogosSection() {
  return (
    <section className="border-y border-border bg-secondary/30 py-12">
      <div className="container mx-auto px-4">
        <p className="mb-8 text-center text-sm font-medium text-muted-foreground">
          신뢰할 수 있는 데이터 소스
        </p>
        <div className="flex flex-wrap items-center justify-center gap-4 md:gap-6">
          <Badge 
            variant="secondary" 
            className="flex items-center gap-2 border border-border bg-card px-4 py-2 text-sm text-muted-foreground"
          >
            <Database className="h-4 w-4 text-primary" />
            식품안전나라 공공API
          </Badge>
          <Badge 
            variant="secondary" 
            className="flex items-center gap-2 border border-border bg-card px-4 py-2 text-sm text-muted-foreground"
          >
            <ClipboardCheck className="h-4 w-4 text-primary" />
            HACCP 기준점 DB
          </Badge>
        </div>
      </div>
    </section>
  )
}
