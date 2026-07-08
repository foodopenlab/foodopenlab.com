import { NextRequest, NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"
import { AGENT_FALLBACKS } from "@/lib/server/food-stats-agent"

export const dynamic = "force-dynamic"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const year = searchParams.get("year")

  try {
    const qs = new URLSearchParams()
    if (year) qs.set("year", year)
    const url = `${getBackendOrigin()}/food-stats/by-agent${qs.toString() ? `?${qs}` : ""}`
    const response = await fetch(url, { cache: "no-store", signal: AbortSignal.timeout(3000) })
    if (response.ok) {
      const bodyText = await response.text()
      return new NextResponse(bodyText, {
        status: response.status,
        headers: { "Content-Type": response.headers.get("content-type") || "application/json" },
      })
    }
  } catch (e) {
    console.warn("[api/food-stats/by-agent] 백엔드 DB 연결 실패, 폴백 수행:", e instanceof Error ? e.message : e)
  }

  const targetYear = year && year !== "all" ? year : null
  const fallbackData = AGENT_FALLBACKS[targetYear || "all"] || AGENT_FALLBACKS["all"]
  return NextResponse.json({ year: targetYear || "전체", data: fallbackData })
}
