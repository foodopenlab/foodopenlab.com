import type {
  FoodStatsByAgentResponse,
  FoodStatsByFacilityResponse,
  FoodStatsYearlyResponse,
  HaccpProductInfo,
  LicenseStatusSearchResponse,
} from "@/lib/types/phase3"

const HACCP_API = "/api/haccp-cert/product-info"
const FOOD_STATS_API = "/api/food-stats"
const LICENSE_API = "/api/license-status/search"

export async function fetchHaccpProductInfo(params: {
  prdlst_report_no?: string
  product_name?: string
}): Promise<HaccpProductInfo | null> {
  const { prdlst_report_no, product_name } = params
  if (!prdlst_report_no?.trim() && !product_name?.trim()) return null

  const qs = new URLSearchParams()
  if (prdlst_report_no?.trim()) qs.set("prdlst_report_no", prdlst_report_no.trim())
  if (product_name?.trim()) qs.set("product_name", product_name.trim())

  const res = await fetch(`${HACCP_API}?${qs.toString()}`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`HACCP 제품 정보 조회 실패: ${res.statusText}`)
  }
  const body = (await res.json()) as HaccpProductInfo
  if (body && typeof body === "object" && body.found) return body
  return null
}

export async function fetchFoodStatsYearly(): Promise<FoodStatsYearlyResponse> {
  const res = await fetch(`${FOOD_STATS_API}/yearly`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`연도별 식품 위해 사고 통계 조회 실패: ${res.statusText}`)
  }
  return (await res.json()) as FoodStatsYearlyResponse
}

export async function fetchFoodStatsByAgent(year: string | null): Promise<FoodStatsByAgentResponse> {
  const qs = new URLSearchParams()
  if (year && year !== "all") qs.set("year", year)
  const q = qs.toString()
  const res = await fetch(`${FOOD_STATS_API}/by-agent${q ? `?${q}` : ""}`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`원인균별 식품 위해 사고 통계 조회 실패: ${res.statusText}`)
  }
  return (await res.json()) as FoodStatsByAgentResponse
}

export async function fetchFoodStatsByFacility(year: string | null): Promise<FoodStatsByFacilityResponse> {
  const qs = new URLSearchParams()
  if (year && year !== "all") qs.set("year", year)
  const q = qs.toString()
  const res = await fetch(`${FOOD_STATS_API}/by-facility${q ? `?${q}` : ""}`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`시설별 식품 위해 사고 통계 조회 실패: ${res.statusText}`)
  }
  return (await res.json()) as FoodStatsByFacilityResponse
}

export async function fetchLicenseStatus(businessName: string): Promise<LicenseStatusSearchResponse | null> {
  const n = businessName.trim()
  if (!n) return null

  const qs = new URLSearchParams({ business_name: n })
  const res = await fetch(`${LICENSE_API}?${qs.toString()}`, { cache: "no-store" })
  if (!res.ok) {
    throw new Error(`인허가 상태 검색 실패: ${res.statusText}`)
  }
  const body = (await res.json()) as LicenseStatusSearchResponse
  if (body && typeof body === "object" && body.found) return body
  return null;
}