import type { RecallListItem } from "@/lib/server/recall-display"

export type RawRecallRow = {
  product_name: string
  reason: string
  business_name: string
  registered_at: string
  recall_grade: string
  food_type: string
  serial_no: string
}

function parseGrade(raw: string): number | null {
  const m = raw.match(/([123])/)
  return m ? Number(m[1]) : null
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

export function rawRowToListItem(row: RawRecallRow): RecallListItem | null {
  const product = (row.product_name || "").trim()
  if (!product) return null
  const serial = (row.serial_no || "").trim()
  const food_type = (row.food_type || "").trim()
  return {
    id: serial || `recall-${product.slice(0, 40)}-${row.registered_at || ""}`,
    product_name: product,
    manufacturer: (row.business_name || "").trim() || "미상",
    food_type: food_type || null,
    food_category: mapFoodCategory(food_type),
    recall_reason: (row.reason || "").trim() || null,
    recall_grade: parseGrade(row.recall_grade || ""),
    recall_method: null,
    registered_at: (row.registered_at || "").trim() || null,
    image_url: null,
    prdlst_report_no: null,
  }
}
