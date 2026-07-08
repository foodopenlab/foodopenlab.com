"use client"

import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { Factory, ShoppingBag, Store, ShieldCheck, Pill, Utensils, FlaskConical } from "lucide-react"

export const COMPANY_TYPE_OPTIONS = [
  "식품제조가공업",
  "즉석판매제조가공업",
  "식품판매업",
  "축산물가공업",
  "건강기능식품제조업",
  "집단급식소",
  "식품첨가물제조업",
] as const

export type CompanyTypeOption = (typeof COMPANY_TYPE_OPTIONS)[number]

type Props = {
  value: string
  onValueChange: (next: string) => void
  disabled?: boolean
  className?: string
}

const SECTOR_METADATA: Record<CompanyTypeOption, { icon: any; desc: string }> = {
  "식품제조가공업": {
    icon: Factory,
    desc: "식품을 제조, 가공하는 업종",
  },
  "즉석판매제조가공업": {
    icon: Store,
    desc: "즉석에서 제조하여 직접 판매",
  },
  "식품판매업": {
    icon: ShoppingBag,
    desc: "식품을 유통, 판매하는 업종",
  },
  "축산물가공업": {
    icon: ShieldCheck,
    desc: "식육, 유가공, 알가공업",
  },
  "건강기능식품제조업": {
    icon: Pill,
    desc: "건강기능식품을 제조하는 업종",
  },
  "집단급식소": {
    icon: Utensils,
    desc: "기숙사, 학교, 병원 등 급식시설",
  },
  "식품첨가물제조업": {
    icon: FlaskConical,
    desc: "감미료, 색소 등 식품첨가물 제조",
  },
}

export function CompanyTypeSelector({ value, onValueChange, disabled, className }: Props) {
  return (
    <div className={cn("space-y-3", className)}>
      <Label className="text-xs font-semibold tracking-wider uppercase text-muted-foreground">업종 선택 (필수)</Label>
      <div className="grid gap-2 max-h-[320px] overflow-y-auto pr-1">
        {COMPANY_TYPE_OPTIONS.map((opt) => {
          const meta = SECTOR_METADATA[opt]
          const Icon = meta.icon
          const isSelected = value === opt
          
          return (
            <button
              key={opt}
              type="button"
              disabled={disabled}
              onClick={() => onValueChange(opt)}
              className={cn(
                "flex items-start gap-3 rounded-xl border p-3 text-left transition-all duration-200 select-none",
                isSelected
                  ? "border-primary bg-primary/10 text-primary ring-1 ring-primary"
                  : "border-border bg-card hover:bg-accent hover:border-accent-foreground/30 text-muted-foreground hover:text-foreground",
                disabled && "opacity-50 cursor-not-allowed"
              )}
            >
              <div className={cn(
                "flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border",
                isSelected ? "border-primary/20 bg-primary/20" : "border-border bg-muted/50"
              )}>
                <Icon className={cn("h-4 w-4", isSelected ? "text-primary" : "text-muted-foreground")} />
              </div>
              <div className="space-y-0.5">
                <div className={cn("text-xs font-semibold leading-none", isSelected ? "text-primary" : "text-foreground")}>
                  {opt}
                </div>
                <div className="text-[10px] text-muted-foreground leading-snug">
                  {meta.desc}
                </div>
              </div>
            </button>
          )
        })}
      </div>
    </div>
  )
}
