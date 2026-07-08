"use client"

import { cn } from "@/lib/utils"
import { ExternalLink } from "lucide-react"

export interface ReportSummaryItem {
  title: string
  url: string
  source: string
  published_at: string
}

export interface ReportSummarySection {
  type: string
  items: ReportSummaryItem[]
  is_empty: boolean
}

export const REPORT_SECTION_META: Record<
  string,
  {
    label: string
    headerClass: string
    linkClass: string
    borderClass: string
    bgClass: string
  }
> = {
  NEWS: {
    label: "[업계뉴스]",
    headerClass: "text-sky-400",
    linkClass: "text-sky-400 hover:text-sky-300",
    borderClass: "border-l-sky-500",
    bgClass: "bg-sky-500/[0.06]",
  },
  RECALL: {
    label: "[회수·행정처분]",
    headerClass: "text-rose-400",
    linkClass: "text-rose-400 hover:text-rose-300",
    borderClass: "border-l-rose-500",
    bgClass: "bg-rose-500/[0.06]",
  },
  LAW: {
    label: "[법규 변동]",
    headerClass: "text-amber-400",
    linkClass: "text-amber-400 hover:text-amber-300",
    borderClass: "border-l-amber-500",
    bgClass: "bg-amber-500/[0.06]",
  },
  MFDS: {
    label: "[식약처 보도자료]",
    headerClass: "text-emerald-400",
    linkClass: "text-emerald-400 hover:text-emerald-300",
    borderClass: "border-l-emerald-500",
    bgClass: "bg-emerald-500/[0.06]",
  },
  RISK: {
    label: "[식중독 위험 현황]",
    headerClass: "text-orange-400",
    linkClass: "text-orange-400 hover:text-orange-300",
    borderClass: "border-l-orange-500",
    bgClass: "bg-orange-500/[0.06]",
  },
  RESEARCH: {
    label: "[최신 연구 동향]",
    headerClass: "text-violet-400",
    linkClass: "text-violet-400 hover:text-violet-300",
    borderClass: "border-l-violet-500",
    bgClass: "bg-violet-500/[0.06]",
  },
  STATS: {
    label: "[식품산업 통계·동향]",
    headerClass: "text-cyan-400",
    linkClass: "text-cyan-400 hover:text-cyan-300",
    borderClass: "border-l-cyan-500",
    bgClass: "bg-cyan-500/[0.06]",
  },
}

const SECTION_ORDER = ["NEWS", "RECALL", "LAW", "MFDS", "RISK", "RESEARCH", "STATS"]

function normalizeType(type: string): string {
  return type.toUpperCase()
}

function formatDate(value: string): string {
  if (!value) return ""
  const head = value.slice(0, 10)
  if (/^\d{4}-\d{2}-\d{2}$/.test(head)) {
    return head.replace(/-/g, ".")
  }
  return value
}

interface ReportSummaryViewProps {
  sections: ReportSummarySection[]
}

export function ReportSummaryView({ sections }: ReportSummaryViewProps) {
  const ordered = SECTION_ORDER.map((type) =>
    sections.find((s) => normalizeType(s.type) === type)
  ).filter(Boolean) as ReportSummarySection[]

  return (
    <div className="space-y-4">
      {ordered.map((section) => {
        const type = normalizeType(section.type)
        const meta = REPORT_SECTION_META[type] ?? {
          label: `[${type}]`,
          headerClass: "text-primary",
          linkClass: "text-primary hover:text-primary/80",
          borderClass: "border-l-primary",
          bgClass: "bg-primary/[0.06]",
        }

        const isEmpty = section.is_empty || section.items.length === 0

        return (
          <section
            key={type}
            className={cn(
              "rounded-lg border border-border/50 border-l-4 p-4 sm:p-5",
              meta.borderClass,
              meta.bgClass
            )}
          >
            <h3
              className={cn(
                "text-base font-bold tracking-tight mb-3 pb-2 border-b border-border/40",
                meta.headerClass
              )}
            >
              {meta.label}
            </h3>

            {isEmpty ? (
              <p className="text-sm text-muted-foreground italic">당일 특이사항 없음</p>
            ) : (
              <ul className="space-y-3">
                {section.items.map((item, idx) => (
                  <li
                    key={idx}
                    className="rounded-md bg-background/40 border border-border/30 px-3 py-2.5 space-y-1"
                  >
                    {item.url ? (
                      <a
                        href={item.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={cn(
                          "inline-flex items-start gap-1.5 text-sm font-semibold leading-snug",
                          "underline underline-offset-[3px] decoration-2",
                          meta.linkClass
                        )}
                      >
                        <span className="flex-1">{item.title}</span>
                        <ExternalLink className="h-3.5 w-3.5 shrink-0 mt-0.5 opacity-70" />
                      </a>
                    ) : (
                      <p className={cn("text-sm font-semibold leading-snug", meta.headerClass)}>
                        {item.title}
                      </p>
                    )}
                    <p className="text-xs text-muted-foreground">
                      {item.source}
                      {item.published_at ? (
                        <span className="text-muted-foreground/70">
                          {" "}
                          · {formatDate(item.published_at)}
                        </span>
                      ) : null}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </section>
        )
      })}
    </div>
  )
}
