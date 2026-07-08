export type RecallGrade = 1 | 2 | 3
export type RecallSource = "domestic" | "imported"

export type RecallItem = {
  id: string
  product_name: string
  manufacturer: string
  food_type: string
  food_category: string
  recall_reason: string
  recall_grade: RecallGrade
  recall_method: string
  registered_at: string
  source: RecallSource
  mfg_date: string
  expiry_date: string
  image_url?: string
  /** Phase 3 — HACCP 인증원 제품이미지·포장지표기 조회용 (선택) */
  prdlst_report_no?: string
  original_url?: string
}

export type RecallQuery = {
  source?: RecallSource | "all"
  food_category?: string
  food_type?: string
  grade?: RecallGrade | "all"
  page?: number
  size?: number
}

export type RecallListResult = {
  total: number
  page: number
  items: RecallItem[]
  display_note?: string | null
}

export const mockRecalls: RecallItem[] = [
  {
    id: "recall-001",
    product_name: "프리미엄 그릭요거트 플레인",
    manufacturer: "한빛유가공",
    food_type: "발효유",
    food_category: "유가공품",
    recall_reason: "대장균군 기준 초과 검출",
    recall_grade: 1,
    recall_method: "판매 중단 및 소비자 반품 안내",
    registered_at: "2026-05-18",
    source: "domestic",
    mfg_date: "2026-05-01",
    expiry_date: "2026-05-28",
    prdlst_report_no: "20180501001234",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-002",
    product_name: "훈제 닭가슴살 슬라이스",
    manufacturer: "푸드웨이브",
    food_type: "양념육",
    food_category: "식육가공품",
    recall_reason: "표시사항 중 알레르기 유발물질 누락",
    recall_grade: 2,
    recall_method: "유통 제품 회수 및 표시 개선",
    registered_at: "2026-05-15",
    source: "domestic",
    mfg_date: "2026-04-22",
    expiry_date: "2026-06-21",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-003",
    product_name: "냉동 망고 다이스",
    manufacturer: "글로벌프룻코리아",
    food_type: "과채가공품",
    food_category: "수입식품",
    recall_reason: "잔류농약 기준 초과",
    recall_grade: 1,
    recall_method: "수입사 회수 및 판매처 공지",
    registered_at: "2026-05-13",
    source: "imported",
    mfg_date: "2026-02-10",
    expiry_date: "2027-02-09",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-004",
    product_name: "현미 누룽지 스낵",
    manufacturer: "바른곡물",
    food_type: "과자",
    food_category: "곡류가공품",
    recall_reason: "금속성 이물 혼입 가능성",
    recall_grade: 2,
    recall_method: "해당 제조번호 전량 회수",
    registered_at: "2026-05-11",
    source: "domestic",
    mfg_date: "2026-04-19",
    expiry_date: "2026-10-18",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-005",
    product_name: "매콤 떡볶이 소스",
    manufacturer: "소스랩",
    food_type: "소스",
    food_category: "조미식품",
    recall_reason: "보존료 사용기준 초과",
    recall_grade: 2,
    recall_method: "판매처 회수 및 소비자 교환",
    registered_at: "2026-05-09",
    source: "domestic",
    mfg_date: "2026-03-25",
    expiry_date: "2027-03-24",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-006",
    product_name: "저당 프로틴바 초코",
    manufacturer: "헬스바이오",
    food_type: "기타가공품",
    food_category: "건강간편식",
    recall_reason: "영양성분 함량 표시 부적합",
    recall_grade: 3,
    recall_method: "표시 정정 및 자율 회수",
    registered_at: "2026-05-06",
    source: "domestic",
    mfg_date: "2026-04-01",
    expiry_date: "2027-04-01",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-007",
    product_name: "수입 냉동 새우살",
    manufacturer: "오션트레이드",
    food_type: "수산물가공품",
    food_category: "수입식품",
    recall_reason: "동물용의약품 기준 초과",
    recall_grade: 1,
    recall_method: "수입 통관 이후 유통분 회수",
    registered_at: "2026-04-29",
    source: "imported",
    mfg_date: "2026-01-12",
    expiry_date: "2028-01-11",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "recall-008",
    product_name: "딸기잼 미니컵",
    manufacturer: "스위트팜",
    food_type: "잼",
    food_category: "당류가공품",
    recall_reason: "용기 밀봉 불량",
    recall_grade: 3,
    recall_method: "소비자 구매처 반품",
    registered_at: "2026-04-25",
    source: "domestic",
    mfg_date: "2026-03-20",
    expiry_date: "2027-03-19",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
]

export function getRecallCategories() {
  return Array.from(new Set(mockRecalls.map((item) => item.food_category)))
}

export function getMockFoodTypes(): string[] {
  return Array.from(new Set(mockRecalls.map((item) => item.food_type).filter(Boolean))).sort()
}

function matchesFoodTypeKeyword(item: RecallItem, keyword: string): boolean {
  const kw = keyword.trim()
  if (!kw) return true
  return item.food_type.includes(kw) || item.food_category.includes(kw)
}

export async function getMockRecalls(query: RecallQuery = {}): Promise<RecallListResult> {
  const { source = "all", food_category = "전체", food_type, grade = "all", page = 1, size = 20 } = query
  const limit = 5

  let items = [...mockRecalls]
  if (source !== "all") items = items.filter((item) => item.source === source)
  if (grade !== "all") items = items.filter((item) => item.recall_grade === grade)

  const kw = (food_type || "").trim()
  if (kw) {
    const matched = items.filter((item) => matchesFoodTypeKeyword(item, kw))
    const pageItems = matched.slice(0, limit)
    if (pageItems.length) {
      return { total: pageItems.length, page: 1, items: pageItems }
    }
    return { total: Math.min(limit, items.length), page: 1, items: items.slice(0, limit), display_note: "mock fallback" }
  }

  if (food_category !== "전체") {
    const matched = items.filter((item) => item.food_category === food_category)
    const pageItems = matched.slice(0, limit)
    if (pageItems.length) {
      return { total: pageItems.length, page: 1, items: pageItems }
    }
    return { total: Math.min(limit, items.length), page: 1, items: items.slice(0, limit), display_note: "mock fallback" }
  }

  if (page <= 1) {
    const pageItems = items.slice(0, limit)
    return { total: items.length, page: 1, items: pageItems }
  }

  const total = items.length
  const start = (page - 1) * size
  return { total, page, items: items.slice(start, start + size) }
}

export function getMockRecallById(id: string) {
  return mockRecalls.find((item) => item.id === id)
}
