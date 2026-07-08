import { NextResponse } from "next/server"
import { getSeoulWeather } from "@/lib/server/weather-seoul"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    return NextResponse.json(await getSeoulWeather())
  } catch (e) {
    console.error("[api/weather/seoul]", e)
    return NextResponse.json(
      { detail: e instanceof Error ? e.message : "날씨 조회 실패" },
      { status: 502 },
    )
  }
}
