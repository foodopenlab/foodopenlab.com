export type EnforcementProcessType = "영업정지" | "영업취소" | "과징금" | "시정명령" | "기타"
export type EnforcementPeriod = "1m" | "3m" | "6m" | "1y"

export type EnforcementItem = {
  id: string
  business_name: string
  business_type: string
  address: string
  process_type: EnforcementProcessType
  violation_content: string
  violation_date: string
  process_date: string
  district: string
  original_url?: string
}

export type EnforcementQuery = {
  process_type?: EnforcementProcessType | "전체"
  business_name?: string
  page?: number
  size?: number
}

export type EnforcementListResult = {
  total: number
  page: number
  items: EnforcementItem[]
  list_max?: number
  empty_label?: string | null
}

export const mockEnforcements: EnforcementItem[] = [
  {
    id: "enf-001",
    business_name: "한빛유가공",
    business_type: "유가공업",
    address: "경기도 화성시 식품안전로 12",
    process_type: "영업정지",
    violation_content: "자가품질검사 부적합 제품 출고",
    violation_date: "2026-05-03",
    process_date: "2026-05-17",
    district: "경기도 화성시",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "enf-002",
    business_name: "푸드웨이브",
    business_type: "식육가공업",
    address: "충청북도 청주시 흥덕구 오송읍",
    process_type: "시정명령",
    violation_content: "작업장 위생관리 기준 미준수",
    violation_date: "2026-05-01",
    process_date: "2026-05-14",
    district: "충청북도 청주시",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "enf-003",
    business_name: "글로벌프룻코리아",
    business_type: "수입식품등 수입판매업",
    address: "인천광역시 중구 공항동로 84",
    process_type: "과징금",
    violation_content: "수입신고 내용과 실제 표시사항 불일치",
    violation_date: "2026-04-23",
    process_date: "2026-05-10",
    district: "인천광역시 중구",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "enf-004",
    business_name: "바른곡물",
    business_type: "식품제조가공업",
    address: "전라북도 익산시 국가식품로 220",
    process_type: "영업정지",
    violation_content: "금속검출 공정 기록 관리 미흡",
    violation_date: "2026-04-20",
    process_date: "2026-05-04",
    district: "전라북도 익산시",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "enf-005",
    business_name: "소스랩",
    business_type: "소스류 제조업",
    address: "서울특별시 금천구 가산디지털2로 31",
    process_type: "시정명령",
    violation_content: "원료 입고검수 기록 일부 누락",
    violation_date: "2026-04-11",
    process_date: "2026-04-29",
    district: "서울특별시 금천구",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
  {
    id: "enf-006",
    business_name: "오션트레이드",
    business_type: "수산물 수입판매업",
    address: "부산광역시 서구 원양로 71",
    process_type: "영업취소",
    violation_content: "부적합 판정 수산물 반복 수입",
    violation_date: "2026-03-26",
    process_date: "2026-04-18",
    district: "부산광역시 서구",
    original_url: "https://www.foodsafetykorea.go.kr",
  },
]

const INITIAL = 5
const MAX_LIST = 20

export async function getMockEnforcements(query: EnforcementQuery = {}): Promise<EnforcementListResult> {
  const { process_type = "전체", business_name = "", page = 1, size = 20 } = query

  let items = [...mockEnforcements].sort((a, b) => b.process_date.localeCompare(a.process_date))
  if (process_type !== "전체") {
    if (process_type === "기타") {
      const main: EnforcementProcessType[] = ["영업정지", "영업취소", "과징금", "시정명령"]
      items = items.filter((item) => !main.includes(item.process_type))
    } else {
      items = items.filter((item) => item.process_type === process_type)
    }
  }
  const kw = business_name.trim()
  if (kw) {
    items = items.filter((item) => item.business_name.includes(kw))
  }

  const total = items.length
  const empty_label = kw && total === 0 ? "사실없음" : null

  if (page <= 1) {
    return {
      total,
      page: 1,
      items: items.slice(0, Math.min(INITIAL, MAX_LIST)),
      list_max: MAX_LIST,
      empty_label,
    }
  }

  const skip = INITIAL + (page - 2) * size
  const limit = Math.min(size, MAX_LIST - skip)
  return {
    total,
    page,
    items: items.slice(skip, skip + limit),
    list_max: MAX_LIST,
    empty_label,
  }
}

export function getMockEnforcementById(id: string) {
  return mockEnforcements.find((item) => item.id === id)
}
