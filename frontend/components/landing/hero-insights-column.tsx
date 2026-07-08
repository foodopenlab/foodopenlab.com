import { LatestRecallsPanel } from "@/components/landing/latest-recalls-panel"
import { LatestSanctionsPanel } from "@/components/landing/latest-sanctions-panel"

/** 히어로 우측: 회수·판매중지 + 행정처분 */
export function HeroInsightsColumn() {
  return (
    <div className="flex w-full min-w-0 flex-col gap-4">
      <LatestRecallsPanel compact />
      <LatestSanctionsPanel compact />
    </div>
  )
}
