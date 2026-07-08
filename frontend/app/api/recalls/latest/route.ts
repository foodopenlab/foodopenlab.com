import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"
import { readJsonSnapshot } from "@/lib/server/read-snapshot"

export const dynamic = "force-dynamic"

type SnapshotItem = {
  product_name?: string
  reason?: string
  business_name?: string
  registered_at?: string
  recall_grade?: string
  food_type?: string
  serial_no?: string
}

type Snapshot = {
  fetched_at?: string | null
  is_today?: boolean
  matched_date?: string | null
  items?: SnapshotItem[]
}

export async function GET() {
  // 1. 백엔드 DB 조회 (FastAPI) — 새벽 스케줄러가 적재한 데이터를 그대로 서빙
  try {
    const response = await fetch(`${getBackendOrigin()}/recalls/latest`, {
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
    console.warn("[api/recalls/latest] 백엔드 DB 연결 실패, 스냅샷 폴백 수행:", e instanceof Error ? e.message : e)
  }

  // 2. 백엔드 연결 실패 시에만 로컬 스냅샷으로 폴백 (외부 공공 API 실시간 호출 없음)
  const snap = await readJsonSnapshot<Snapshot>("recall_snapshot.json")
  return NextResponse.json({
    items: snap?.items ?? [],
    fetched_at: snap?.fetched_at ?? null,
    query_date: null,
    is_today: Boolean(snap?.is_today),
    matched_date: snap?.matched_date ?? null,
    source: "식품안전나라",
  })
}
