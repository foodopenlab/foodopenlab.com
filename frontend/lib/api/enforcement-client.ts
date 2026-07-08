import type { EnforcementItem, EnforcementListResult, EnforcementQuery } from "@/lib/mocks/enforcement"

type ApiEnforcement = {
  id: string
  business_name: string
  business_type?: string | null
  address?: string | null
  process_type?: string | null
  violation_content?: string | null
  violation_date?: string | null
  process_date?: string | null
  district?: string | null
}

const PT = ["영업정지", "영업취소", "과징금", "시정명령"] as const

function mapProcessType(v: string | null | undefined): EnforcementItem["process_type"] {
  const s = (v ?? "").trim()
  if (PT.includes(s as (typeof PT)[number])) return s as EnforcementItem["process_type"]
  for (const pt of PT) {
    if (s.includes(pt)) return pt
  }
  return "기타"
}

export function mapApiEnforcementToItem(row: ApiEnforcement): EnforcementItem {
  return {
    id: row.id,
    business_name: row.business_name,
    business_type: row.business_type ?? "",
    address: row.address ?? "",
    process_type: mapProcessType(row.process_type),
    violation_content: row.violation_content ?? "",
    violation_date: row.violation_date ?? "",
    process_date: row.process_date ?? "",
    district: row.district ?? "",
    original_url: "https://www.foodsafetykorea.go.kr",
  }
}

export async function fetchEnforcementList(query: EnforcementQuery): Promise<EnforcementListResult> {
  const { process_type = "전체", business_name = "", page = 1, size = 20 } = query
  const qs = new URLSearchParams()
  qs.set("page", String(page))
  qs.set("size", String(size))
  if (business_name.trim()) qs.set("business_name", business_name.trim())
  if (process_type && process_type !== "전체") qs.set("process_type", process_type)

  const res = await fetch(`/api/enforcement?${qs.toString()}`, { cache: "no-store" })
  if (!res.ok) {
    const text = await res.text().catch(() => "")
    const detail =
      text.trimStart().startsWith("<") || !text.trim()
        ? "행정처분 API 요청에 실패했습니다."
        : text
    throw new Error(`(${res.status}) ${detail}`)
  }
  const data = (await res.json()) as {
    total: number
    page: number
    items: ApiEnforcement[]
    list_max?: number
    empty_label?: string | null
    last_sync_at?: string | null
  }
  return {
    total: data.total,
    page: data.page,
    items: (data.items ?? []).map(mapApiEnforcementToItem),
    list_max: data.list_max ?? 20,
    empty_label: data.empty_label ?? null,
  }
}

export async function fetchEnforcementDetail(id: string): Promise<EnforcementItem | null> {
  const res = await fetch(`/api/enforcement/${encodeURIComponent(id)}`, { cache: "no-store" })
  if (!res.ok) {
    if (res.status === 404) return null
    const text = await res.text().catch(() => "")
    const detail =
      text.trimStart().startsWith("<") || !text.trim()
        ? "행정처분 상세 조회에 실패했습니다."
        : text
    throw new Error(`(${res.status}) ${detail}`)
  }
  const row = (await res.json()) as ApiEnforcement
  return mapApiEnforcementToItem(row)
}
