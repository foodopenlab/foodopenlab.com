import { NextResponse } from "next/server"

import { resolveBackendOrigin } from "@/lib/backend-origin.mjs"

const BACKEND_MISSING_DETAIL =
  "인증·마이페이지 API는 공개 FastAPI 서버가 필요합니다. " +
  "Vercel 환경 변수 BACKEND_URL에 HTTPS API 주소를 설정한 뒤 재배포해 주세요."

type ProxyToBackendOptions = {
  backendPath: string
  request: Request
  timeoutMs?: number
}

export async function proxyToBackend({
  backendPath,
  request,
  timeoutMs = 60_000,
}: ProxyToBackendOptions): Promise<Response> {
  const origin = resolveBackendOrigin()
  if (!origin) {
    return NextResponse.json({ detail: BACKEND_MISSING_DETAIL }, { status: 503 })
  }

  const incomingUrl = new URL(request.url)
  const target = `${origin}${backendPath}${incomingUrl.search}`

  const headers = new Headers()
  const contentType = request.headers.get("content-type")
  if (contentType) headers.set("Content-Type", contentType)
  const authorization = request.headers.get("authorization")
  if (authorization) headers.set("Authorization", authorization)

  const method = request.method.toUpperCase()
  const hasBody = method !== "GET" && method !== "HEAD"

  try {
    const upstream = await fetch(target, {
      method,
      headers,
      body: hasBody ? await request.text() : undefined,
      cache: "no-store",
      signal: AbortSignal.timeout(timeoutMs),
    })

    const bodyText = await upstream.text()
    return new NextResponse(bodyText, {
      status: upstream.status,
      headers: { "Content-Type": upstream.headers.get("content-type") || "application/json" },
    })
  } catch {
    return NextResponse.json(
      {
        detail:
          "백엔드에 연결할 수 없습니다. FastAPI 서버 상태와 Vercel BACKEND_URL을 확인해 주세요.",
      },
      { status: 502 },
    )
  }
}
