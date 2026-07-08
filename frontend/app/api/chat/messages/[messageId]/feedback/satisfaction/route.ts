import { NextResponse } from "next/server"
import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"

export const dynamic = "force-dynamic"

export async function POST(request: Request, { params }: { params: Promise<{ messageId: string }> }) {
  const { messageId } = await params
  const origin = resolveBackendOrigin()
  if (!origin) {
    return NextResponse.json({ detail: "백엔드 DB 연결이 필요합니다." }, { status: 503 })
  }

  const target = `${origin}/messages/${encodeURIComponent(messageId)}/feedback/satisfaction`
  const body = await request.text()

  const res = await fetch(target, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    cache: "no-store",
  })

  return new NextResponse(await res.text(), {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  })
}
