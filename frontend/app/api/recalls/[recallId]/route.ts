import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"

export const dynamic = "force-dynamic"

type Params = { params: Promise<{ recallId: string }> }

export async function GET(_request: Request, { params }: Params) {
  const { recallId } = await params

  try {
    const response = await fetch(`${getBackendOrigin()}/recalls/${encodeURIComponent(recallId)}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })
    const bodyText = await response.text()
    return new NextResponse(bodyText, {
      status: response.status,
      headers: { "Content-Type": response.headers.get("content-type") || "application/json" },
    })
  } catch (e) {
    console.error("[api/recalls/[recallId]]", e)
    return NextResponse.json(
      { detail: e instanceof Error ? e.message : "회수 상세 조회 실패" },
      { status: 502 },
    )
  }
}
