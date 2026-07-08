/** Phase 3 — API 응답 타입 (백엔드 연동 시 스키마 일치). 프론트 mock 폴백 동일 구조. */

export type HaccpProductInfo = {
  found: boolean
  prdlst_report_no: string
  product_name: string | null
  manufacturer: string | null
  raw_materials: string[]
  allergens: string[]
  nutrient_info: string | null
  image_urls: string[]
  barcode: string | null
}

export type FoodStatsYearlyRow = {
  year: string
  total_incidents: number
  total_patients: number
}

export type FoodStatsYearlyResponse = {
  data: FoodStatsYearlyRow[]
}

export type FoodStatsByDimensionRow = {
  agent?: string
  facility?: string
  incidents: number
  patients: number
}

export type FoodStatsByAgentResponse = {
  year: string | "전체"
  data: { agent: string; incidents: number; patients: number }[]
}

export type FoodStatsByFacilityResponse = {
  year: string | "전체"
  data: { facility: string; incidents: number; patients: number }[]
}

export type LicenseStatusItem = {
  business_name: string
  license_number: string | null
  status: "영업중" | "휴업" | "폐업" | "기타"
  status_code: string | null
  business_type: string | null
  licensed_date: string | null
  address: string | null
  last_changed_date: string | null
}

export type LicenseStatusSearchResponse = {
  business_name: string
  found: boolean
  total: number
  items: LicenseStatusItem[]
}
