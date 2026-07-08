import { NextResponse } from "next/server"
import { getLatestSanctionsResponse } from "@/lib/server/food-safety-sanction"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    return NextResponse.json(await getLatestSanctionsResponse())
  } catch (e) {
    console.error("[api/sanctions/latest]", e)
    return NextResponse.json(
      { detail: e instanceof Error ? e.message : "행정처분 정보 조회 실패" },
      { status: 502 },
    )
  }
}
