import type { ReactNode } from "react"
import { Badge } from "@/components/ui/badge"
import { FoodPoisoningStatsPanel } from "@/components/landing/food-poisoning-stats-panel"
import { HeroInsightsColumn } from "@/components/landing/hero-insights-column"

type HeroSectionProps = {
  geminiChat?: ReactNode
  insightsColumn?: ReactNode
}

export function HeroSection({ geminiChat, insightsColumn }: HeroSectionProps) {
  const showSidebar = Boolean(geminiChat || insightsColumn)

  return (
    <section className="relative py-12 sm:py-20 md:py-32">
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden">
        <div className="absolute left-1/2 top-0 h-[500px] w-[800px] max-w-[200vw] -translate-x-1/2 rounded-full bg-primary/10 blur-3xl" />
      </div>

      <div className="container mx-auto min-w-0 max-w-[min(100%,90rem)] px-4 sm:px-6 lg:px-8">
        <div
          className={
            showSidebar
              ? "grid min-w-0 items-stretch gap-8 sm:gap-10 lg:grid-cols-[minmax(0,1.2fr)_minmax(300px,400px)] lg:gap-10 xl:gap-12"
              : "grid min-w-0 items-center gap-12"
          }
        >
          <div className="mx-auto flex h-full w-full min-w-0 flex-col items-center text-center lg:mx-0 lg:items-start lg:text-left">
            <Badge variant="secondary" className="mb-4 max-w-full text-center text-xs sm:mb-6 sm:text-sm">
              식품안전나라 공공 API 연동
            </Badge>

            <h1 className="mb-4 text-balance text-3xl font-bold leading-snug tracking-tight text-foreground sm:mb-6 sm:text-4xl sm:leading-tight md:text-5xl lg:text-6xl">
              위해식품 회수 정보를
              <br />
              <span className="text-primary">AI가</span> <span className="text-primary">실시간 모니터링</span> 합니다.
            </h1>

            <p className="mb-6 max-w-prose text-pretty text-base text-muted-foreground sm:text-lg md:mb-8 md:text-xl">
              원료명을 입력하면 HACCP 관리점까지 자동으로 분석해드립니다.
            </p>

            {geminiChat ? (
              <div className="flex min-h-0 w-full min-w-0 flex-1 flex-col gap-5">
                <div className="w-full shrink-0">{geminiChat}</div>
                <FoodPoisoningStatsPanel variant="hero" className="w-full" />
              </div>
            ) : null}
          </div>

          {showSidebar ? (
            <aside className="w-full min-w-0 lg:sticky lg:top-24 lg:self-start">
              {insightsColumn ?? <HeroInsightsColumn />}
            </aside>
          ) : null}
        </div>
      </div>
    </section>
  )
}
