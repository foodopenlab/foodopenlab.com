export type ActorType = "expert" | "anonymous";

export type FeedbackLabel = "correct" | "partial" | "incorrect";

export interface RecallItem {
  id: string;
  product_name: string;
  manufacturer: string;
  food_type: string;
  food_category: string;
  recall_reason: string;
  recall_grade: string;
  recall_method: string;
  registered_at: string;
  image_url?: string | null;
  prdlst_report_no?: string | null;
}

export interface EnforcementItem {
  id: string;
  business_name: string;
  industry: string;
  disposition_date: string;
  disposition_start?: string | null;
  disposition_type: string;
  violation: string;
  address: string;
  representative: string;
  disposition_detail: string;
  agency: string;
  serial_no: string;
  category: string;
  service_id: string;
}

export interface HaccpCertItem {
  found: boolean;
  prdlst_report_no: string;
  product_name: string | null;
  manufacturer: string | null;
  raw_materials: string[];
  allergens: string[];
  nutrient_info: string | null;
  image_urls: string[];
  barcode: string | null;
}
