"use client"

import { useState } from "react"
import Link from "next/link"
import { AlertTriangle, CheckCircle2, Factory, FileCheck, ShieldCheck, XCircle } from "lucide-react"
import { RiskLevelBadge } from "@/components/supplier/risk-level-badge"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import type { SupplierRiskCard } from "@/lib/mocks/supplier"
import { cn } from "@/lib/utils"

export function RiskCard({ data }: { data: SupplierRiskCard }) {
  const [expanded, setExpanded] = useState(false)
  const products = expanded ? data.products : data.products.slice(0, 5)
  const hiddenCount = Math.max(0, data.products.length - products.length)

  return (
    <article className="space-y-5 rounded-2xl border border-border/70 bg-card/60 p-5 shadow-sm md:p-6">
      <header className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <div className="flex flex-wrap items-center gap-2">
            <h2 className="text-xl font-semibold text-foreground">{data.business_name}</h2>
            <RiskLevelBadge level={data.risk_score.level} />
          </div>
          <ul className="mt-3 space-y-1 text-sm text-muted-foreground">
            {data.risk_score.reasons.map((reason) => (
              <li key={reason}>- {reason}</li>
            ))}
          </ul>
        </div>
      </header>

      <div className="grid gap-3 lg:grid-cols-3">
        <StatusPanel icon={<FileCheck className="h-5 w-5 text-primary" />} title="인허가 현황">
          <p className={cn("font-medium", data.license_status.status === "폐업" && "text-red-300", data.license_status.status === "휴업" && "text-orange-300")}>
            {data.license_status.status ?? "미조회"}
          </p>
          <p>허가번호: {data.license_status.license_number ?? "-"}</p>
          <p>허가일: {data.license_status.licensed_date ?? "-"}</p>
          <p className="line-clamp-2">주소: {data.license_status.address ?? "-"}</p>
        </StatusPanel>

        <StatusPanel icon={<ShieldCheck className="h-5 w-5 text-primary" />} title="HACCP 인증">
          <div className="flex items-center gap-2">
            {data.haccp_status.certified ? (
              <CheckCircle2 className="h-4 w-4 text-emerald-300" />
            ) : (
              <XCircle className="h-4 w-4 text-red-300" />
            )}
            <span className={cn("font-medium", data.haccp_status.certified ? "text-emerald-300" : "text-red-300")}>
              {data.haccp_status.certified ? "인증" : "미인증"}
            </span>
            {isExpiringSoon(data.haccp_status.expiry_date) ? (
              <Badge variant="outline" className="border-orange-500/30 bg-orange-500/15 text-orange-300">
                곧 만료
              </Badge>
            ) : null}
          </div>
          <p>지정번호: {data.haccp_status.certificate_number ?? "-"}</p>
          <p>유효기간: {data.haccp_status.expiry_date ?? "-"}</p>
          <p>
            품목: {formatLimitedList(data.haccp_status.certified_products, 3)}
          </p>
        </StatusPanel>

        <StatusPanel icon={<AlertTriangle className="h-5 w-5 text-primary" />} title="행정처분 이력">
          {data.enforcement_summary.total_count === 0 ? (
            <p className="font-medium text-emerald-300">처분 이력 없음</p>
          ) : (
            <>
              <p className="font-medium text-orange-300">{data.enforcement_summary.total_count}건 확인</p>
              <p>최근 처분: {data.enforcement_summary.recent_type ?? "-"}</p>
              <p>최근 일자: {data.enforcement_summary.recent_date ?? "-"}</p>
            </>
          )}
          <Link href={`/enforcement?business_name=${encodeURIComponent(data.business_name)}`} className="inline-flex text-primary hover:underline">
            /enforcement 조회 →
          </Link>
        </StatusPanel>
      </div>

      <section>
        <div className="flex items-center gap-2">
          <Factory className="h-5 w-5 text-primary" />
          <h3 className="font-semibold text-foreground">제조 품목</h3>
        </div>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          {products.map((product) => (
            <div key={`${product.product_name}-${product.reported_date}`} className="rounded-xl border border-border/60 bg-background/50 p-4">
              <p className="font-medium text-foreground">{product.product_name}</p>
              <p className="mt-1 text-sm text-muted-foreground">
                {product.food_type} · 신고 {product.reported_date}
              </p>
              <div className="mt-3 flex flex-wrap gap-1.5">
                {product.raw_materials.slice(0, 3).map((material) => (
                  <Badge key={material} variant="secondary" className="text-[11px]">
                    {material}
                  </Badge>
                ))}
              </div>
            </div>
          ))}
        </div>
        {hiddenCount > 0 ? (
          <Button type="button" variant="outline" className="mt-3" onClick={() => setExpanded(true)}>
            더 보기 (+{hiddenCount}개)
          </Button>
        ) : null}
      </section>
    </article>
  )
}

function StatusPanel({ icon, title, children }: { icon: React.ReactNode; title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border border-border/60 bg-background/50 p-4 text-sm text-muted-foreground">
      <div className="mb-3 flex items-center gap-2 text-foreground">
        {icon}
        <h3 className="font-semibold">{title}</h3>
      </div>
      <div className="space-y-1.5">{children}</div>
    </section>
  )
}

function formatLimitedList(items: string[], limit: number) {
  if (!items.length) return "-"
  const visible = items.slice(0, limit)
  const rest = items.length - visible.length
  return `${visible.join(", ")}${rest > 0 ? ` 외 ${rest}개` : ""}`
}

function isExpiringSoon(value: string | null) {
  if (!value) return false
  const expiry = new Date(value)
  const today = new Date("2026-05-19")
  const diff = expiry.getTime() - today.getTime()
  return diff > 0 && diff <= 90 * 24 * 60 * 60 * 1000
}
