"use client"

import Link from "next/link"
import { AlertTriangle, Building2, CheckCircle2, Scale, ShieldAlert, ShieldCheck, XCircle } from "lucide-react"
import { GradeBadge } from "@/components/recalls/grade-badge"
import { ProcessBadge } from "@/components/enforcement/process-badge"
import { RiskLevelBadge, riskLevelDescription } from "@/components/supplier/risk-level-badge"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import type { EnforcementProcessType } from "@/lib/mocks/enforcement"
import type { RecallGrade } from "@/lib/mocks/recalls"
import type { SupplierRiskCard } from "@/lib/types/supplier"
import { formatRegisteredDate } from "@/lib/utils"

type Props = {
  data: SupplierRiskCard
}

function asRecallGrade(g: number | null | undefined): RecallGrade | null {
  if (g === 1 || g === 2 || g === 3) return g
  return null
}

export function SupplierRiskCardView({ data }: Props) {
  const gradeCounts = { high: 0, medium: 0, low: 0 }
  const haccp = data.haccp_certification
  const haccpLabel = haccp?.found ? (haccp.certified ? "인증" : "미인증") : "미조회"
  for (const r of data.recalls) {
    const g = r.recall_grade
    if (g === 1) gradeCounts.high += 1
    else if (g === 2) gradeCounts.medium += 1
    else if (g === 3) gradeCounts.low += 1
  }

  return (
    <div className="space-y-6">
      <Card className="border-border/70 bg-card/60">
        <CardHeader className="pb-3">
          <div className="flex flex-wrap items-start justify-between gap-3">
            <div className="space-y-1">
              <CardTitle className="flex items-center gap-2 text-xl">
                <Building2 className="h-5 w-5 text-primary" aria-hidden />
                {data.business_name}
              </CardTitle>
              <CardDescription>{data.summary}</CardDescription>
            </div>
            <div className="text-right">
              <RiskLevelBadge level={data.overall_risk} />
              <p className="mt-1 text-xs text-muted-foreground">{riskLevelDescription(data.overall_risk)}</p>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {gradeCounts.high > 0 && (
              <Badge className="bg-red-500/20 text-red-400 hover:bg-red-500/30">HIGH {gradeCounts.high}건</Badge>
            )}
            {gradeCounts.medium > 0 && (
              <Badge className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30">
                MEDIUM {gradeCounts.medium}건
              </Badge>
            )}
            {gradeCounts.low > 0 && (
              <Badge className="bg-green-500/20 text-green-400 hover:bg-green-500/30">LOW {gradeCounts.low}건</Badge>
            )}
            <Badge variant="outline" className="text-muted-foreground">
              회수 {data.recall_count}건 · 처분 {data.enforcement_count}건
            </Badge>
          </div>
        </CardContent>
      </Card>

      {data.license?.found && (
        <Card className="border-border/70 bg-card/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-base">인허가 (데모)</CardTitle>
            {data.license.demo && (
              <CardDescription>실연동 전 데모 데이터입니다. 공공 API 연동 시 교체됩니다.</CardDescription>
            )}
          </CardHeader>
          <CardContent className="flex flex-wrap gap-2 text-sm">
            <Badge variant="secondary">{data.license.status ?? "-"}</Badge>
            {data.license.business_type && <span className="text-muted-foreground">{data.license.business_type}</span>}
            {data.license.license_number && (
              <span className="text-muted-foreground">허가번호 {data.license.license_number}</span>
            )}
          </CardContent>
        </Card>
      )}

      {haccp && (
        <Card className="border-border/70 bg-card/50">
          <CardHeader className="pb-2">
            <CardTitle className="flex items-center gap-2 text-base">
              <ShieldCheck className="h-4 w-4 text-primary" aria-hidden />
              HACCP 인증
            </CardTitle>
            {haccp.demo && (
              <CardDescription>실제 인증 API 연동 전 데모 인증정보입니다.</CardDescription>
            )}
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex flex-wrap items-center gap-2">
              {haccp.certified ? (
                <CheckCircle2 className="h-4 w-4 text-emerald-300" aria-hidden />
              ) : (
                <XCircle className={haccp.found ? "h-4 w-4 text-red-300" : "h-4 w-4 text-muted-foreground"} aria-hidden />
              )}
              <Badge
                variant="outline"
                className={
                  haccp.certified
                    ? "border-emerald-500/40 bg-emerald-500/15 text-emerald-300"
                    : haccp.found
                      ? "border-red-500/40 bg-red-500/15 text-red-300"
                      : "border-border bg-muted/30 text-muted-foreground"
                }
              >
                {haccpLabel}
              </Badge>
              {haccp.certificate_number && (
                <span className="text-muted-foreground">지정번호 {haccp.certificate_number}</span>
              )}
            </div>
            <div className="flex flex-wrap gap-3 text-muted-foreground">
              {haccp.designated_date && (
                <span>지정일 {formatRegisteredDate(haccp.designated_date)}</span>
              )}
              {haccp.expiry_date && (
                <span>유효기간 {formatRegisteredDate(haccp.expiry_date)}</span>
              )}
            </div>
            {haccp.certified_products.length > 0 && (
              <div className="flex flex-wrap gap-1.5">
                {haccp.certified_products.slice(0, 5).map((product) => (
                  <Badge key={product} variant="secondary" className="text-xs">
                    {product}
                  </Badge>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      )}

      <section className="space-y-3">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <ShieldAlert className="h-5 w-5 text-primary" aria-hidden />
          회수 이력
          <span className="text-sm font-normal text-muted-foreground">({data.recall_count}건)</span>
        </h2>
        {data.recalls.length === 0 ? (
          <p className="text-sm text-muted-foreground">제조사명 일치 회수 캐시가 없습니다.</p>
        ) : (
          <ul className="space-y-2">
            {data.recalls.map((r) => {
              const grade = asRecallGrade(r.recall_grade)
              return (
                <li key={r.id}>
                  <Link
                    href={`/recalls/${r.id}`}
                    className="block rounded-xl border border-border/70 bg-card/50 p-3 transition-colors hover:border-primary/40"
                  >
                    <div className="flex flex-wrap items-center gap-2">
                      {grade != null && <GradeBadge grade={grade} />}
                      <span className="font-medium text-foreground">{r.product_name}</span>
                      <span className="text-xs text-muted-foreground">{formatRegisteredDate(r.registered_at)}</span>
                    </div>
                    {r.recall_reason && (
                      <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{r.recall_reason}</p>
                    )}
                  </Link>
                </li>
              )
            })}
          </ul>
        )}
      </section>

      <section className="space-y-3">
        <h2 className="flex items-center gap-2 text-lg font-semibold text-foreground">
          <Scale className="h-5 w-5 text-primary" aria-hidden />
          행정처분
          <span className="text-sm font-normal text-muted-foreground">({data.enforcement_count}건)</span>
        </h2>
        {data.enforcements.length === 0 ? (
          <p className="text-sm text-muted-foreground">업체명 일치 행정처분 캐시가 없습니다.</p>
        ) : (
          <ul className="space-y-2">
            {data.enforcements.map((e) => (
              <li key={e.id}>
                <Link
                  href={`/enforcement/${e.id}`}
                  className="block rounded-xl border border-border/70 bg-card/50 p-3 transition-colors hover:border-primary/40"
                >
                  <div className="flex flex-wrap items-center gap-2">
                    <ProcessBadge processType={(e.process_type ?? "기타") as EnforcementProcessType} />
                    <span className="text-xs text-muted-foreground">{formatRegisteredDate(e.process_date) || "-"}</span>
                  </div>
                  {e.violation_content && (
                    <p className="mt-1 line-clamp-2 text-sm text-muted-foreground">{e.violation_content}</p>
                  )}
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>

      <p className="flex items-start gap-2 rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-xs text-muted-foreground">
        <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden />
        MVP: DB 캐시의 제조사명·업체명 부분 일치 검색입니다. 공급망·MRL·규격 API는 추후 연동됩니다.
      </p>
    </div>
  )
}
