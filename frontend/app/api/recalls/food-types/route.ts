import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"

export const dynamic = "force-dynamic"

export async function GET() {
  try {
    const response = await fetch(`${getBackendOrigin()}/recalls/food-types`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })
    const bodyText = await response.text()
    return new NextResponse(bodyText, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") || "application/json" },
    })
  } catch (e) {
    console.error("[api/recalls/food-types]", e)
    return NextResponse.json(
      { detail: e instanceof Error ? e.message : "식품유형 목록 조회 실패" },
      { status: 502 },
    )
  }
}
