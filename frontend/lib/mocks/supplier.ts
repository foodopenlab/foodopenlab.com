export type RiskLevel = "green" | "yellow" | "red"

export type SupplierRiskCard = {
  business_name: string
  license_status: {
    found: boolean
    license_number: string | null
    address: string | null
    status: "영업중" | "휴업" | "폐업" | "미조회" | null
    licensed_date: string | null
    type: "식품제조가공업" | "축산물가공업" | null
  }
  haccp_status: {
    certified: boolean
    certificate_number: string | null
    expiry_date: string | null
    designated_date: string | null
    certified_products: string[]
  }
  products: Array<{
    product_name: string
    food_type: string
    reported_date: string
    raw_materials: string[]
  }>
  risk_score: {
    level: RiskLevel
    reasons: string[]
  }
  enforcement_summary: {
    total_count: number
    recent_type: string | null
    recent_date: string | null
  }
}

export const mockSupplierRiskCards: SupplierRiskCard[] = [
  {
    business_name: "한빛유가공",
    license_status: {
      found: true,
      license_number: "2026-가공-00124",
      address: "경기도 화성시 식품안전로 12",
      status: "영업중",
      licensed_date: "2021-03-15",
      type: "식품제조가공업",
    },
    haccp_status: {
      certified: true,
      certificate_number: "HACCP-DAIRY-2024-112",
      expiry_date: "2027-06-30",
      designated_date: "2024-07-01",
      certified_products: ["발효유", "그릭요거트"],
    },
    products: [
      {
        product_name: "프리미엄 그릭요거트 플레인",
        food_type: "발효유",
        reported_date: "2025-01-22",
        raw_materials: ["원유", "유산균", "탈지분유"],
      },
      {
        product_name: "저지방 딸기요거트",
        food_type: "발효유",
        reported_date: "2025-06-03",
        raw_materials: ["원유", "딸기농축액", "유산균"],
      },
    ],
    risk_score: {
      level: "green",
      reasons: ["영업상태 정상", "HACCP 인증 유효", "최근 행정처분 이력 없음"],
    },
    enforcement_summary: {
      total_count: 0,
      recent_type: null,
      recent_date: null,
    },
  },
  {
    business_name: "푸드웨이브",
    license_status: {
      found: true,
      license_number: "2022-식육-00891",
      address: "충청북도 청주시 흥덕구 오송읍",
      status: "영업중",
      licensed_date: "2022-09-02",
      type: "축산물가공업",
    },
    haccp_status: {
      certified: true,
      certificate_number: "HACCP-MEAT-2023-045",
      expiry_date: "2026-07-12",
      designated_date: "2023-07-13",
      certified_products: ["훈제 닭가슴살", "양념육", "분쇄가공육"],
    },
    products: [
      {
        product_name: "훈제 닭가슴살 슬라이스",
        food_type: "양념육",
        reported_date: "2024-11-10",
        raw_materials: ["닭가슴살", "정제소금", "혼합제제"],
      },
      {
        product_name: "바질 닭가슴살 큐브",
        food_type: "분쇄가공육",
        reported_date: "2025-02-18",
        raw_materials: ["닭고기", "바질", "마늘분말"],
      },
      {
        product_name: "저염 훈제닭",
        food_type: "양념육",
        reported_date: "2025-08-01",
        raw_materials: ["닭고기", "로즈마리", "정제수"],
      },
    ],
    risk_score: {
      level: "yellow",
      reasons: ["HACCP 인증 유효기간 90일 이내 만료 예정", "최근 2년 내 시정명령 1건"],
    },
    enforcement_summary: {
      total_count: 1,
      recent_type: "시정명령",
      recent_date: "2026-05-14",
    },
  },
  {
    business_name: "오션트레이드",
    license_status: {
      found: true,
      license_number: "2020-수산-00331",
      address: "부산광역시 서구 원양로 71",
      status: "휴업",
      licensed_date: "2020-04-20",
      type: "식품제조가공업",
    },
    haccp_status: {
      certified: false,
      certificate_number: null,
      expiry_date: null,
      designated_date: null,
      certified_products: [],
    },
    products: [
      {
        product_name: "수입 냉동 새우살",
        food_type: "수산물가공품",
        reported_date: "2024-02-12",
        raw_materials: ["새우", "정제수", "구연산"],
      },
    ],
    risk_score: {
      level: "red",
      reasons: ["휴업 상태", "HACCP 미인증", "최근 1년 내 영업정지 포함 행정처분 2건"],
    },
    enforcement_summary: {
      total_count: 2,
      recent_type: "영업정지",
      recent_date: "2026-04-18",
    },
  },
]

export async function fetchSupplierRiskCard(name: string): Promise<SupplierRiskCard | null> {
  const keyword = name.trim().toLowerCase()
  if (!keyword) return null

  await new Promise((resolve) => setTimeout(resolve, 350))

  return (
    mockSupplierRiskCards.find((card) => card.business_name.toLowerCase().includes(keyword)) ??
    mockSupplierRiskCards.find((card) => keyword.includes(card.business_name.toLowerCase())) ??
    null
  )
}
