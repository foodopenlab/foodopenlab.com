"use client"

import { Badge } from "@/components/ui/badge"

export type ReferencedLaw = {
  law_name: string
  article: string
}

type Props = {
  laws: ReferencedLaw[]
  className?: string
}

export function LawReferenceBadge({ laws, className }: Props) {
  if (!laws.length) return null
  return (
    <div className={className}>
      <p className="mb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground/80">
        ⚖️ 참조 법정 (클릭 시 국가법령정보센터로 이동)
      </p>
      <div className="flex flex-wrap gap-1.5">
        {laws.map((law, i) => {
          const cleanArticle = (law.article || "").trim()
          const hasArticle = cleanArticle && cleanArticle !== "(조문번호 미상)"
          const url = hasArticle
            ? `https://www.law.go.kr/법령/${encodeURIComponent(law.law_name)}/${encodeURIComponent(cleanArticle)}`
            : `https://www.law.go.kr/법령/${encodeURIComponent(law.law_name)}`
          return (
            <a
              key={`${law.law_name}-${law.article}-${i}`}
              href={url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 rounded-md border border-border/80 bg-secondary/80 px-2.5 py-1 text-xs text-secondary-foreground hover:bg-secondary hover:text-primary hover:border-primary/50 transition-all shadow-sm cursor-pointer"
            >
              <span>{law.law_name} {law.article}</span>
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.8}
                stroke="currentColor"
                className="h-3 w-3 opacity-60"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M13.5 6H5.25A2.25 2.25 0 0 0 3 8.25v10.5A2.25 2.25 0 0 0 5.25 21h10.5A2.25 2.25 0 0 0 18 18.75V10.5m-10.5 6L21 3m0 0h-5.25M21 3v5.25"
                />
              </svg>
            </a>
          )
        })}
      </div>
    </div>
  )
}
