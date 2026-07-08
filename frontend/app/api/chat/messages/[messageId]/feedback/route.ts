import { NextResponse } from "next/server"
import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"

export const dynamic = "force-dynamic"

function backendUrl(messageId: string, search = "") {
  const origin = resolveBackendOrigin()
  if (!origin) return null
  return `${origin}/chat/messages/${encodeURIComponent(messageId)}/feedback${search}`
}

export async function GET(request: Request, { params }: { params: Promise<{ messageId: string }> }) {
  const { messageId } = await params
  const url = new URL(request.url)
  const target = backendUrl(messageId, url.search)
  if (!target) {
    return NextResponse.json(null)
  }

  const res = await fetch(target, { cache: "no-store" })
  return new NextResponse(await res.text(), {
    status: res.status,
    headers: { "Content-Type": "application/json" },
  })
}

export async function POST(request: Request, { params }: { params: Promise<{ messageId: string }> }) {
  const { messageId } = await params
  const target = backendUrl(messageId)
  if (!target) {
    return NextResponse.json({ detail: "백엔드 DB 연결이 필요합니다." }, { status: 503 })
  }

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
