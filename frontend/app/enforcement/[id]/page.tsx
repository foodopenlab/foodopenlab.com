"use client"

import Link from "next/link"
import { useParams, useRouter } from "next/navigation"
import { useEffect, useState } from "react"
import { ArrowLeft, ExternalLink, Printer } from "lucide-react"
import { InfoRow } from "@/components/recalls/info-row"
import { ProcessBadge } from "@/components/enforcement/process-badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { fetchEnforcementDetail } from "@/lib/api/enforcement-client"
import type { EnforcementItem } from "@/lib/mocks/enforcement"
import { formatRegisteredDate } from "@/lib/utils"

export default function EnforcementDetailPage() {
  const router = useRouter()
  const params = useParams<{ id: string }>()
  const [item, setItem] = useState<EnforcementItem | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    const id = params.id
    if (!id) {
      setLoading(false)
      return
    }
    setLoading(true)
    void (async () => {
      const row = await fetchEnforcementDetail(id)
      if (!cancelled) {
        setItem(row)
        setLoading(false)
      }
    })()
    return () => {
      cancelled = true
    }
  }, [params.id])

  if (loading) {
    return (
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-4 py-10">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-48 w-full rounded-2xl" />
      </main>
    )
  }

  if (!item) {
    return (
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-4 py-10">
        <Button type="button" variant="ghost" className="w-fit" asChild>
          <Link href="/enforcement">
            <ArrowLeft className="mr-2 h-4 w-4" />
            목록으로
          </Link>
        </Button>
        <div className="rounded-2xl border border-border/70 bg-card/60 p-8 text-center text-muted-foreground">행정처분 정보를 찾을 수 없습니다.</div>
      </main>
    )
  }

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Button type="button" variant="ghost" asChild>
          <Link href="/enforcement">
            <ArrowLeft className="mr-2 h-4 w-4" />
            목록으로
          </Link>
        </Button>
        <Button type="button" variant="outline" onClick={() => window.print()}>
          <Printer className="mr-2 h-4 w-4" />
          인쇄
        </Button>
      </div>

      <section className="rounded-2xl border border-border/70 bg-card/60 p-5 md:p-6">
        <div className="flex flex-wrap items-center gap-2">
          <ProcessBadge processType={item.process_type} />
          <h1 className="text-2xl font-semibold text-foreground">{item.business_name}</h1>
        </div>
        <p className="mt-2 text-sm text-muted-foreground">처분확정일 {formatRegisteredDate(item.process_date)}</p>
        <p className="mt-2 text-sm text-muted-foreground">
          {item.business_type} · {item.district}
        </p>
        <p className="mt-4 text-sm leading-relaxed text-foreground/90">{item.violation_content}</p>
      </section>

      <section className="rounded-2xl border border-border/70 bg-card/60 p-5 md:p-6">
        <h2 className="text-base font-semibold text-primary">상세</h2>
        <dl className="mt-3">
          <InfoRow label="업종">{item.business_type}</InfoRow>
          <InfoRow label="주소">{item.address}</InfoRow>
          <InfoRow label="위반일시">{formatRegisteredDate(item.violation_date)}</InfoRow>
          <InfoRow label="담당 지자체">{item.district}</InfoRow>
        </dl>
      </section>

      <section className="rounded-2xl border border-border/70 bg-card/40 p-5 text-sm text-muted-foreground">
        <p>데이터 출처 | 식품안전나라 (mfds.go.kr)</p>
        <Link href={item.original_url ?? "https://www.foodsafetykorea.go.kr"} target="_blank" className="mt-3 inline-flex items-center gap-1 text-primary hover:underline">
          식품안전나라에서 확인
          <ExternalLink className="h-3 w-3" />
        </Link>
      </section>
    </main>
  )
}
