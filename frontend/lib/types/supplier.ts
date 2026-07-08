export type SupplierRiskLevel = "HIGH" | "MEDIUM" | "LOW" | "NONE"

export type SupplierRiskRecallBrief = {
  id: string
  product_name: string
  manufacturer?: string
  recall_grade?: number | null
  registered_at?: string | null
  recall_reason?: string | null
}

export type SupplierRiskEnforcementBrief = {
  id: string
  business_name?: string
  process_type?: string | null
  process_date?: string | null
  violation_content?: string | null
}

export type SupplierLicenseBrief = {
  found: boolean
  status?: string | null
  business_type?: string | null
  license_number?: string | null
  demo?: boolean
}

export type SupplierHaccpCertificationBrief = {
  found: boolean
  certified: boolean
  certificate_number?: string | null
  expiry_date?: string | null
  designated_date?: string | null
  certified_products: string[]
  demo?: boolean
}

export type SupplierRiskCard = {
  business_name: string
  overall_risk: SupplierRiskLevel
  summary: string
  recall_count: number
  enforcement_count: number
  recalls: SupplierRiskRecallBrief[]
  enforcements: SupplierRiskEnforcementBrief[]
  license?: SupplierLicenseBrief | null
  haccp_certification?: SupplierHaccpCertificationBrief | null
}
