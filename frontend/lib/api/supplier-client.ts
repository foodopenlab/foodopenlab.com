import type { SupplierRiskCard } from "@/lib/types/supplier"

export async function fetchSupplierRiskCard(businessName: string): Promise<SupplierRiskCard> {
  const q = new URLSearchParams({ business_name: businessName.trim(), limit: "10" })
  const res = await fetch(`/api/supplier/risk-card?${q.toString()}`, { cache: "no-store" })
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    const detail = typeof body?.detail === "string" ? body.detail : "리스크 카드를 불러오지 못했습니다."
    throw new Error(detail)
  }
  return (await res.json()) as SupplierRiskCard
}
