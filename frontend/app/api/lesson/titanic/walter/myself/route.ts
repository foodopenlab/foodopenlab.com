import { NextResponse } from "next/server"

import { getBackendOrigin } from "@/lib/backend-origin"

export const dynamic = "force-dynamic"

export async function GET() {
  const backendUrl = `${getBackendOrigin()}/api/titanic/walter/myself`

  try {
    const upstream = await fetch(backendUrl, {
      cache: "no-store",
      signal: AbortSignal.timeout(15_000),
    })
    const bodyText = await upstream.text()
    const contentType = upstream.headers.get("content-type") || "application/json"
    return new NextResponse(bodyText, {
      status: upstream.status,
      headers: { "Content-Type": contentType },
    })
  } catch {
    return NextResponse.json(
      {
        detail:
          "백엔드에 연결할 수 없습니다. com.auditor에서 uvicorn(8000)이 실행 중인지 확인하세요.",
      },
      { status: 503 },
    )
  }
}
