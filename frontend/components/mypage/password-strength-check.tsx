import { Check, X } from "lucide-react"
import { cn } from "@/lib/utils"

interface PasswordStrengthCheckProps {
  hasLength: boolean
  hasSpecial: boolean
}

export function PasswordStrengthCheck({ hasLength, hasSpecial }: PasswordStrengthCheckProps) {
  return (
    <div className="p-3 bg-muted/30 border border-border/40 rounded-lg space-y-2 text-xs">
      <p className="font-semibold text-muted-foreground mb-1">새 비밀번호 보안 요구사항:</p>
      
      {/* 8+ characters requirement */}
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[9px] font-bold transition-all duration-200",
            hasLength
              ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
              : "bg-destructive/10 text-destructive border-destructive/30"
          )}
        >
          {hasLength ? <Check className="h-2.5 w-2.5" /> : <X className="h-2.5 w-2.5" />}
        </div>
        <span className={cn("font-medium transition-colors duration-200", hasLength ? "text-emerald-500" : "text-muted-foreground")}>
          8자 이상 입력
        </span>
      </div>

      {/* Special character requirement */}
      <div className="flex items-center gap-2">
        <div
          className={cn(
            "flex h-4 w-4 shrink-0 items-center justify-center rounded-full border text-[9px] font-bold transition-all duration-200",
            hasSpecial
              ? "bg-emerald-500/10 text-emerald-500 border-emerald-500/30"
              : "bg-destructive/10 text-destructive border-destructive/30"
          )}
        >
          {hasSpecial ? <Check className="h-2.5 w-2.5" /> : <X className="h-2.5 w-2.5" />}
        </div>
        <span className={cn("font-medium transition-colors duration-200", hasSpecial ? "text-emerald-500" : "text-muted-foreground")}>
          특수문자 1개 이상 포함 (!@#$%^&* 등)
        </span>
      </div>
    </div>
  )
}
