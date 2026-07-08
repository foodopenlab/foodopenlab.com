import type { RecallGrade, RecallItem, RecallListResult, RecallQuery, RecallSource } from "@/lib/mocks/recalls"
import { getMockFoodTypes, getMockRecallById, getMockRecalls } from "@/lib/mocks/recalls"

type ApiRecall = {
  id: string
  product_name: string
  manufacturer: string
  food_type?: string | null
  food_category?: string | null
  recall_reason?: string | null
  recall_grade?: number | null
  recall_method?: string | null
  registered_at?: string | null
  image_url?: string | null
  prdlst_report_no?: string | null
}

type LatestRecallRow = {
  product_name?: string
  reason?: string
  business_name?: string
  registered_at?: string
  recall_grade?: string
  food_type?: string
  serial_no?: string
}

function inferSource(foodCategory: string): RecallSource {
  return foodCategory.includes("수입") ? "imported" : "domestic"
}

function parseGrade(raw: string | number | null | undefined): RecallGrade {
  if (typeof raw === "number" && raw >= 1 && raw <= 3) return raw as RecallGrade
  const m = String(raw ?? "").match(/([123])/)
  return m ? (Number(m[1]) as RecallGrade) : 3
}

export function mapApiRecallToItem(row: ApiRecall): RecallItem {
  const food_category = row.food_category ?? ""
  const g = parseGrade(row.recall_grade)
  return {
    id: row.id,
    product_name: row.product_name,
    manufacturer: row.manufacturer,
    food_type: row.food_type ?? "",
    food_category: food_category || "기타",
    recall_reason: row.recall_reason ?? "",
    recall_grade: g,
    recall_method: row.recall_method ?? "",
    registered_at: row.registered_at ?? "",
    source: inferSource(food_category),
    mfg_date: "",
    expiry_date: "",
    image_url: row.image_url ?? undefined,
    prdlst_report_no: row.prdlst_report_no ?? undefined,
    original_url: "https://www.foodsafetykorea.go.kr",
  }
}

function mapLatestRowToItem(row: LatestRecallRow): RecallItem | null {
  const product = (row.product_name || "").trim()
  if (!product) return null
  const serial = (row.serial_no || "").trim()
  const id = serial || `recall-${product.slice(0, 40)}-${row.registered_at || ""}`
  const food_type = row.food_type ?? ""
  const food_category =
    food_type.includes("수입") ? "수입식품" : food_type.includes("가공") || food_type.includes("유") ? "유가공품" : "기타"
  return {
    id,
    product_name: product,
    manufacturer: row.business_name ?? "미상",
    food_type,
    food_category,
    recall_reason: row.reason ?? "",
    recall_grade: parseGrade(row.recall_grade),
    recall_method: "",
    registered_at: row.registered_at ?? "",
    source: inferSource(food_category),
    mfg_date: "",
    expiry_date: "",
    original_url: "https://www.foodsafetykorea.go.kr",
  }
}

const SEARCH_LIMIT = 5
const MAX_ITEMS_ALL = 100

function applyClientFilters(items: RecallItem[], query: RecallQuery): RecallListResult {
  const { food_category = "전체", food_type, grade = "all", page = 1, size = 20 } = query
  let rows = [...items]
  if (grade !== "all") rows = rows.filter((r) => r.recall_grade === grade)

  const kw = (food_type || "").trim()
  if (kw) {
    const matched = rows.filter(
      (r) => r.food_type.includes(kw) || r.food_category.includes(kw),
    )
    const picked = matched.slice(0, SEARCH_LIMIT)
    if (picked.length) return { total: picked.length, page: 1, items: picked }
    const fallback = rows.slice(0, SEARCH_LIMIT)
    return {
      total: fallback.length,
      page: 1,
      items: fallback,
      display_note: fallback.length ? "입력한 식품유형과 일치하는 항목이 없어 최근 회수를 표시합니다." : null,
    }
  }

  if (food_category && food_category !== "전체") {
    const matched = rows.filter((r) => r.food_category === food_category)
    const picked = matched.slice(0, SEARCH_LIMIT)
    if (picked.length) return { total: picked.length, page: 1, items: picked }
    const fallback = rows.slice(0, SEARCH_LIMIT)
    return {
      total: fallback.length,
      page: 1,
      items: fallback,
      display_note: fallback.length ? "입력한 식품유형과 일치하는 항목이 없어 최근 회수를 표시합니다." : null,
    }
  }

  const sorted = [...rows].sort((a, b) =>
    (b.registered_at || "").localeCompare(a.registered_at || ""),
  )
  const isGradeOnly = grade !== "all" && (!food_category || food_category === "전체")

  if (isGradeOnly) {
    const capped = sorted.slice(0, size)
    const start = (page - 1) * size
    return { total: capped.length, page, items: capped.slice(start, start + size) }
  }

  const cappedAll = sorted.slice(0, MAX_ITEMS_ALL)
  if (page <= 1) {
    const picked = cappedAll.slice(0, SEARCH_LIMIT)
    return { total: cappedAll.length, page: 1, items: picked }
  }

  const skip = SEARCH_LIMIT + (page - 2) * size
  return { total: cappedAll.length, page, items: cappedAll.slice(skip, skip + size) }
}

async function fetchRecallListFromLatest(query: RecallQuery): Promise<RecallListResult | null> {
  try {
    const res = await fetch("/api/recalls/latest", { cache: "no-store" })
    if (!res.ok) return null
    const data = (await res.json()) as { items?: LatestRecallRow[] }
    const mapped = (data.items ?? []).map(mapLatestRowToItem).filter((x): x is RecallItem => x !== null)
    if (!mapped.length) return null
    return applyClientFilters(mapped, query)
  } catch {
    return null
  }
}

async function parseJsonResponse(res: Response): Promise<unknown> {
  const raw = await res.text()
  if (!raw.trim()) return null
  try {
    return JSON.parse(raw) as unknown
  } catch {
    throw new Error(raw.slice(0, 200) || res.statusText)
  }
}

export async function fetchRecallFoodTypes(): Promise<string[]> {
  try {
    const res = await fetch("/api/recalls/food-types", { cache: "no-store" })
    if (!res.ok) return getMockFoodTypes()
    const data = (await parseJsonResponse(res)) as { items?: string[] }
    const items = (data.items ?? []).map((t) => String(t).trim()).filter(Boolean)
    return items.length ? items : getMockFoodTypes()
  } catch {
    return getMockFoodTypes()
  }
}

export async function fetchRecallList(query: RecallQuery = {}): Promise<RecallListResult> {
  const { food_category = "전체", food_type, grade = "all", page = 1, size = 20 } = query
  const qs = new URLSearchParams()
  qs.set("page", String(page))
  qs.set("size", String(size))
  const kw = (food_type || "").trim()
  if (kw) qs.set("food_type", kw)
  else if (food_category && food_category !== "전체") qs.set("food_category", food_category)
  if (grade !== "all") qs.set("grade", String(grade))

  try {
    const res = await fetch(`/api/recalls?${qs.toString()}`, { cache: "no-store" })
    const data = await parseJsonResponse(res)
    if (!res.ok) {
      const latest = await fetchRecallListFromLatest(query)
      if (latest) return latest
      return getMockRecalls(query)
    }
    const body = data as { total: number; page: number; items: ApiRecall[]; display_note?: string | null }
    const result: RecallListResult = {
      total: body.total ?? 0,
      page: body.page ?? page,
      items: (body.items ?? []).map(mapApiRecallToItem),
      display_note: body.display_note ?? null,
    }
    if (result.total === 0 && !kw && food_category === "전체" && grade === "all") {
      const latest = await fetchRecallListFromLatest(query)
      if (latest && latest.total > 0) return latest
    }
    return result
  } catch {
    const latest = await fetchRecallListFromLatest(query)
    if (latest) return latest
    return getMockRecalls(query)
  }
}

export async function fetchRecallDetail(id: string): Promise<RecallItem | null> {
  try {
    const res = await fetch(`/api/recalls/${encodeURIComponent(id)}`, { cache: "no-store" })
    if (res.ok) {
      const row = (await parseJsonResponse(res)) as ApiRecall
      return mapApiRecallToItem(row)
    }
  } catch {
    /* fall through */
  }

  const latest = await fetchRecallListFromLatest({ page: 1, size: 50 })
  const hit = latest?.items.find((r) => r.id === id)
  if (hit) return hit

  return getMockRecallById(id) ?? null
}
