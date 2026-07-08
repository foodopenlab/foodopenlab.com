/** 회수 목록 표시 정책 (백엔드 `recall_display.py` 와 동일). */

export const RECALL_TOP_PER_TYPE = 5
export const RECALL_MAX_ALL = 100
export const RECALL_MAX_GRADE = 20

export const DISPLAY_FALLBACK_NOTE =
  "입력한 식품유형과 일치하는 항목이 없어, 등급 조건에 맞는 최근 회수 5건을 표시합니다."

export type RecallListItem = {
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

const UI_CATEGORIES = [
  "유가공품",
  "식육가공품",
  "수입식품",
  "곡류가공품",
  "조미식품",
  "건강간편식",
  "당류가공품",
] as const

const CATEGORY_HINTS: Record<string, string[]> = {
  수입식품: ["수입"],
  식육가공품: ["식육", "육류"],
  곡류가공품: ["곡"],
  조미식품: ["조미"],
  건강간편식: ["건강", "간편"],
  당류가공품: ["당", "잼", "과자", "빵"],
  유가공품: ["유가", "유제품", "가공"],
}

function mapFoodCategory(foodType: string): string {
  const t = foodType.trim()
  if (!t) return "기타"
  if (t.includes("수입")) return "수입식품"
  if (t.includes("식육") || t.includes("육류")) return "식육가공품"
  if (t.includes("곡")) return "곡류가공품"
  if (t.includes("조미")) return "조미식품"
  if (t.includes("건강") || t.includes("간편")) return "건강간편식"
  if (t.includes("당") || t.includes("잼") || t.includes("과자") || t.includes("빵")) return "당류가공품"
  if (t.includes("유") || t.includes("가공") || t.includes("유가") || t.includes("유제품")) return "유가공품"
  return t
}

function sortKey(registeredAt: string | null | undefined): string {
  return (registeredAt ?? "").trim()
}

function gradeFilter(items: RecallListItem[], grade: number | undefined): RecallListItem[] {
  if (grade == null) return items
  return items.filter((r) => r.recall_grade === grade)
}

function sortLatest(items: RecallListItem[]): RecallListItem[] {
  return [...items].sort((a, b) => sortKey(b.registered_at).localeCompare(sortKey(a.registered_at)))
}

function matchesCategory(item: RecallListItem, category: string): boolean {
  const cat = category.trim()
  if (!cat || cat === "전체") return true
  if ((item.food_category ?? "").trim() === cat) return true
  const ft = (item.food_type ?? "").trim()
  if (!ft) return false
  if (mapFoodCategory(ft) === cat) return true
  for (const hint of CATEGORY_HINTS[cat] ?? []) {
    if (ft.includes(hint)) return true
  }
  return false
}

function matchesFoodTypeKeyword(item: RecallListItem, keyword: string): boolean {
  const kw = keyword.trim()
  if (!kw) return true
  const ft = item.food_type ?? ""
  const fc = item.food_category ?? ""
  if (ft.includes(kw) || fc.includes(kw)) return true
  if ((UI_CATEGORIES as readonly string[]).includes(kw)) return matchesCategory(item, kw)
  return false
}

function pickLatest(
  items: RecallListItem[],
  limit: number,
  matcher: (r: RecallListItem) => boolean,
): RecallListItem[] {
  return sortLatest(items.filter(matcher)).slice(0, limit)
}

export function pickRecallDisplaySchemas(
  items: RecallListItem[],
  opts: {
    food_category?: string | null
    food_type?: string | null
    grade?: number | null
    page: number
    size: number
  },
): { items: RecallListItem[]; total: number; display_note: string | null } {
  const { food_category, food_type, grade, page, size } = opts
  const filtered = gradeFilter(items, grade ?? undefined)
  const limit = RECALL_TOP_PER_TYPE

  const kw = (food_type ?? "").trim()
  if (kw) {
    let pageItems = pickLatest(filtered, limit, (r) => matchesFoodTypeKeyword(r, kw))
    let note: string | null = null
    if (!pageItems.length) {
      pageItems = sortLatest(filtered).slice(0, limit)
      if (pageItems.length) note = DISPLAY_FALLBACK_NOTE
    }
    return { items: pageItems, total: pageItems.length, display_note: note }
  }

  const cat = (food_category ?? "").trim()
  if (cat && cat !== "전체") {
    let pageItems = pickLatest(filtered, limit, (r) => matchesCategory(r, cat))
    let note: string | null = null
    if (!pageItems.length) {
      pageItems = sortLatest(filtered).slice(0, limit)
      if (pageItems.length) note = DISPLAY_FALLBACK_NOTE
    }
    return { items: pageItems, total: pageItems.length, display_note: note }
  }

  const allSorted = sortLatest(filtered)
  if (grade != null) {
    const capped = allSorted.slice(0, RECALL_MAX_GRADE)
    const start = (page - 1) * size
    return {
      items: capped.slice(start, start + size),
      total: capped.length,
      display_note: null,
    }
  }

  const cappedAll = allSorted.slice(0, RECALL_MAX_ALL)
  if (page <= 1) {
    return { items: cappedAll.slice(0, limit), total: cappedAll.length, display_note: null }
  }

  const skip = RECALL_TOP_PER_TYPE + (page - 2) * size
  return {
    items: cappedAll.slice(skip, skip + size),
    total: cappedAll.length,
    display_note: null,
  }
}
