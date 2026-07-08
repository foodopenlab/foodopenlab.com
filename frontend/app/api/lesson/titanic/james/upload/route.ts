import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"

export const dynamic = "force-dynamic"
export const maxDuration = 120

export async function POST(request: Request) {
  let form: FormData
  try {
    form = await request.formData()
  } catch {
    return NextResponse.json({ detail: "multipart/form-data를 읽을 수 없습니다." }, { status: 400 })
  }

  const file = form.get("file")
  if (!file || typeof file === "string") {
    return NextResponse.json({ detail: "file 필드(CSV)가 필요합니다." }, { status: 400 })
  }

  const outbound = new FormData()
  const name = file instanceof File ? file.name : "upload.csv"
  outbound.append("file", file, name)

  const backendUrl = `${getBackendOrigin()}/api/titanic/james/upload`

  try {
    const upstream = await fetch(backendUrl, {
      method: "POST",
      body: outbound,
      cache: "no-store",
      signal: AbortSignal.timeout(120_000),
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
          "백엔드(FastAPI 8000)에 연결할 수 없습니다. backend에서 python main.py 실행 여부를 확인하세요.",
      },
      { status: 502 },
    )
  }
}
