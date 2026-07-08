import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"
import { FOOD_STATS_YEARLY_FALLBACK } from "@/lib/server/food-stats-yearly"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const response = await fetch(`${getBackendOrigin()}/food-stats/yearly`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })
    if (response.ok) {
      const bodyText = await response.text()
      return new NextResponse(bodyText, {
        status: response.status,
        headers: { "Content-Type": response.headers.get("content-type") || "application/json" },
      })
    }
  } catch (e) {
    console.warn("[api/food-stats/yearly] 백엔드 DB 연결 실패, 폴백 수행:", e instanceof Error ? e.message : e)
  }

  return NextResponse.json({ data: FOOD_STATS_YEARLY_FALLBACK })
}
