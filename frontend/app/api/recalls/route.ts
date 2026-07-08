import { NextResponse } from "next/server"
import { getBackendOrigin } from "@/lib/backend-origin"
import { readJsonSnapshot } from "@/lib/server/read-snapshot"
import { rawRowToListItem } from "@/lib/server/recalls-catalog"
import { pickRecallDisplaySchemas } from "@/lib/server/recall-display"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)

  const page = Math.max(1, Number(searchParams.get("page") || "1") || 1)
  const size = Math.min(100, Math.max(1, Number(searchParams.get("size") || "20") || 20))
  const food_category = searchParams.get("food_category")
  const food_type = searchParams.get("food_type")
  const gradeRaw = searchParams.get("grade")
  const grade =
    gradeRaw != null && gradeRaw !== "" ? Number(gradeRaw) : null

  // 1. 백엔드 DB 조회 (FastAPI) — 새벽 스케줄러가 적재한 데이터를 그대로 서빙
  try {
    const qs = new URLSearchParams()
    qs.set("page", String(page))
    qs.set("size", String(size))
    if (food_category && food_category !== "전체") qs.set("food_category", food_category)
    if (food_type) qs.set("food_type", food_type)
    if (grade != null && Number.isFinite(grade)) qs.set("grade", String(grade))

    const backendUrl = `${getBackendOrigin()}/recalls?${qs.toString()}`

    // 백엔드가 꺼져 있거나 지연될 경우 빠르게 로컬 스냅샷으로 폴백하도록 3초 타임아웃 적용
    const response = await fetch(backendUrl, {
      cache: "no-store",
      signal: AbortSignal.timeout(3000),
    })

    if (response.ok) {
      const data = await response.json()
      // 백엔드로부터 응답을 성공적으로 수신했으면 즉시 반환
      if (data && typeof data === "object" && "items" in data) {
        return NextResponse.json(data)
      }
    }
  } catch (e) {
    console.warn("[api/recalls] 백엔드 DB 연결 실패, 스냅샷 폴백 수행:", e instanceof Error ? e.message : e)
  }

  // 2. 백엔드 연결 실패 시에만 로컬 스냅샷으로 폴백 (외부 공공 API 실시간 호출 없음)
  try {
    const snap = await readJsonSnapshot<{
      items?: Array<{
        product_name: string
        reason: string
        business_name: string
        registered_at: string
        recall_grade: string
        food_type: string
        serial_no: string
      }>
    }>("recall_snapshot.json")

    const mapped = (snap?.items ?? [])
      .map((r) =>
        rawRowToListItem({
          product_name: r.product_name,
          reason: r.reason,
          business_name: r.business_name,
          registered_at: r.registered_at,
          recall_grade: r.recall_grade,
          food_type: r.food_type,
          serial_no: r.serial_no,
        }),
      )
      .filter((x): x is NonNullable<ReturnType<typeof rawRowToListItem>> => x !== null)

    const result = pickRecallDisplaySchemas(mapped, {
      food_category,
      food_type,
      grade: Number.isFinite(grade) ? grade : null,
      page,
      size,
    })

    return NextResponse.json(result)
  } catch (e) {
    console.error("[api/recalls] 로컬 폴백 최종 실패:", e)
    return NextResponse.json(
      { detail: e instanceof Error ? e.message : "회수 목록 조회 실패" },
      { status: 502 },
    )
  }
}
