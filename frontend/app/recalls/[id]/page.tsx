"use client"

import type { ReactNode } from "react"
import Image from "next/image"
import Link from "next/link"
import { useParams } from "next/navigation"
import { useEffect, useState } from "react"
import { ArrowLeft, ChevronDown, ChevronUp, ExternalLink, ImageIcon, Printer, ShieldAlert } from "lucide-react"
import { InfoRow } from "@/components/recalls/info-row"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Skeleton } from "@/components/ui/skeleton"
import { fetchHaccpProductInfo } from "@/lib/phase3-client"
import { fetchRecallDetail } from "@/lib/api/recalls-client"
import type { HaccpProductInfo } from "@/lib/types/phase3"
import type { RecallItem } from "@/types/api"
import { formatRegisteredDate } from "@/lib/utils"

export default function RecallDetailPage() {
  const params = useParams<{ id: string }>()
  const [item, setItem] = useState<RecallItem | null>(null)
  const [detailLoading, setDetailLoading] = useState(true)
  const [haccp, setHaccp] = useState<HaccpProductInfo | null>(null)
  const [haccpLoading, setHaccpLoading] = useState(false)
  const [rawExpanded, setRawExpanded] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    const id = params.id
    if (!id) {
      setDetailLoading(false)
      return
    }
    setDetailLoading(true)
    setError(null)
    void (async () => {
      try {
        const row = await fetchRecallDetail(id)
        if (!cancelled) {
          setItem(row)
          setDetailLoading(false)
        }
      } catch (err) {
        if (!cancelled) {
          setError("위해 정보를 가져오지 못했습니다. 삭제되었거나 존재하지 않는 항목입니다.")
          setDetailLoading(false)
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [params.id])

  const showHaccpFetch = Boolean(
    item && (item.prdlst_report_no?.trim() || item.product_name?.trim()),
  )

  useEffect(() => {
    if (!item || !showHaccpFetch) {
      setHaccp(null)
      setHaccpLoading(false)
      return
    }
    let cancelled = false
    setHaccpLoading(true)
    void (async () => {
      try {
        const info = await fetchHaccpProductInfo({
          prdlst_report_no: item.prdlst_report_no || undefined,
          product_name: item.product_name || undefined,
        })
        if (!cancelled) {
          setHaccp(info)
          setHaccpLoading(false)
        }
      } catch {
        if (!cancelled) {
          setHaccp(null)
          setHaccpLoading(false)
        }
      }
    })()
    return () => {
      cancelled = true
    }
  }, [item, showHaccpFetch])

  if (detailLoading) {
    return (
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-10">
        <Skeleton className="h-10 w-40" />
        <Skeleton className="h-64 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
      </main>
    )
  }

  if (error || !item) {
    return (
      <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-4 px-4 py-10">
        <Button type="button" variant="ghost" className="w-fit cursor-pointer" asChild>
          <Link href="/recalls">
            <ArrowLeft className="mr-2 h-4 w-4" />
            위해 리포트 목록
          </Link>
        </Button>
        <div className="rounded-xl border border-destructive/20 bg-destructive/10 p-8 text-center text-destructive font-medium">
          {error || "회수 제품 정보를 찾을 수 없습니다."}
        </div>
      </main>
    )
  }

  const displayImageUrl = item.image_url ?? (haccp?.image_urls?.[0] || "")

  const getGradeBadge = (g: string | number | null | undefined) => {
    const gradeStr = String(g ?? "")
    const clean = gradeStr.replace(/[^0-9]/g, "")
    if (clean === "1") {
      return (
        <Badge variant="outline" className="border-red-500 bg-red-500/10 text-red-500 font-extrabold gap-1 py-1 px-3 text-sm">
          🚨 1등급 (위해성 극대)
        </Badge>
      )
    } else if (clean === "2") {
      return (
        <Badge variant="outline" className="border-amber-500 bg-amber-500/10 text-amber-500 font-extrabold gap-1 py-1 px-3 text-sm">
          ⚠️ 2등급 (위해성 중요)
        </Badge>
      )
    } else {
      return (
        <Badge variant="outline" className="border-blue-500 bg-blue-500/10 text-blue-500 font-extrabold gap-1 py-1 px-3 text-sm">
          ℹ️ 3등급 (위해성 보 통)
        </Badge>
      )
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-4xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <div className="flex flex-wrap items-center justify-between gap-3 border-b border-border/50 pb-4">
        <Button type="button" variant="ghost" className="cursor-pointer" asChild>
          <Link href="/recalls">
            <ArrowLeft className="mr-2 h-4 w-4" />
            목록으로 돌아가기
          </Link>
        </Button>
        <Button type="button" variant="outline" className="cursor-pointer shadow-sm" onClick={() => window.print()}>
          <Printer className="mr-2 h-4 w-4" />
          리포트 출력
        </Button>
      </div>

      <header className="rounded-xl border border-border bg-card overflow-hidden shadow-sm flex flex-col md:flex-row">
        <div className="md:w-1/3 h-52 md:h-auto relative bg-muted flex items-center justify-center border-b md:border-b-0 md:border-r border-border shrink-0">
          {displayImageUrl ? (
            <Image 
              src={displayImageUrl} 
              alt={item.product_name} 
              fill
              className="object-cover"
              sizes="(max-w-768px) 100vw, 30vw"
            />
          ) : (
            <div className="text-center text-muted-foreground p-6">
              <ImageIcon className="mx-auto h-12 w-12 text-muted-foreground/55" />
              <p className="mt-2 text-xs font-semibold">제품 식별 이미지 없음</p>
            </div>
          )}
        </div>
        <div className="p-6 md:p-8 flex-1 flex flex-col justify-between gap-4">
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              {getGradeBadge(item.recall_grade)}
              <Badge variant="secondary" className="font-mono text-[10px] md:text-xs">
                품목코드: {item.prdlst_report_no || "정보 미보유"}
              </Badge>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-foreground leading-tight">{item.product_name}</h1>
            <p className="text-sm text-muted-foreground">
              유형: <span className="text-foreground font-semibold">{item.food_type}</span> | 대분류: <span className="text-foreground font-semibold">{item.food_category}</span>
            </p>
          </div>
          <div className="text-xs text-muted-foreground bg-muted/20 border border-border/40 p-3 rounded-lg leading-relaxed">
            📢 <strong>회수 공고 요약</strong>: 해당 제품은 공공 안전 검사 결과에 따른 법령 위반 처분 조치 대상으로 유통 및 판매 행위가 즉시 제한됩니다.
          </div>
        </div>
      </header>

      <div className="grid gap-6 md:grid-cols-2">
        <DetailSection title="⚠️ 위해 및 제재 조치 내역">
          <InfoRow label="회수 사유">{item.recall_reason}</InfoRow>
          <InfoRow label="조치 방법">{item.recall_method}</InfoRow>
          <InfoRow label="회수 등급">{item.recall_grade}</InfoRow>
          <InfoRow label="등록 일자">{item.registered_at ? item.registered_at.slice(0, 10) : "-"}</InfoRow>
        </DetailSection>

        <DetailSection title="🏢 제조 생산처 세부 정보">
          <InfoRow label="제조 업체">{item.manufacturer || "정보 미제공"}</InfoRow>
          <InfoRow label="생산 분류">{item.food_category}</InfoRow>
          <InfoRow label="생산 유형">{item.food_type}</InfoRow>
          <InfoRow label="품목 보고 번호">{item.prdlst_report_no || "미보유"}</InfoRow>
        </DetailSection>
      </div>

      {haccpLoading ? (
        <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <ShieldAlert className="size-5 text-primary animate-pulse" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="mt-3 h-4 w-full max-w-md" />
        </section>
      ) : null}

      {haccp ? (
        <section className="rounded-xl border border-border bg-card p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-border/80 pb-3">
            <h2 className="text-lg font-bold text-primary flex items-center gap-2">
              <ShieldAlert className="size-5 text-primary" />
              HACCP 인증원 제품 상세 분석
            </h2>
            <Badge variant="outline" className="border-primary/30 text-primary font-semibold">
              실시간 원재료 연동
            </Badge>
          </div>

          <div className="space-y-4">
            <div>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">함유 원재료 리스트</h3>
              <div className="flex flex-wrap gap-1.5">
                {(rawExpanded ? haccp.raw_materials : haccp.raw_materials.slice(0, 8)).map((m) => (
                  <Badge key={m} variant="secondary" className="font-semibold text-xs py-0.5 px-2 bg-muted/80 text-muted-foreground">
                    {m}
                  </Badge>
                ))}
                {haccp.raw_materials.length > 8 ? (
                  <Button 
                    type="button" 
                    variant="ghost" 
                    size="sm" 
                    className="h-7 px-2 text-xs font-bold cursor-pointer" 
                    onClick={() => setRawExpanded((v) => !v)}
                  >
                    {rawExpanded ? (
                      <>
                        원재료 접기 <ChevronUp className="ml-1 h-3 w-3" />
                      </>
                    ) : (
                      <>
                        외 {haccp.raw_materials.length - 8}개 더보기 <ChevronDown className="ml-1 h-3 w-3" />
                      </>
                    )}
                  </Button>
                ) : null}
              </div>
            </div>

            <div>
              <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">유해/알레르기 유발 항원</h3>
              <div className="flex flex-wrap gap-1.5">
                {haccp.allergens.length === 0 ? (
                  <p className="text-xs text-muted-foreground font-medium">검출된 알레르기 유발 유발 물질 없음</p>
                ) : (
                  haccp.allergens.map((a) => (
                    <Badge key={a} variant="outline" className="border-orange-500/30 bg-orange-500/10 text-orange-500 font-extrabold text-xs py-0.5 px-2.5">
                      {a}
                    </Badge>
                  ))
                )}
              </div>
            </div>

            {haccp.nutrient_info ? (
              <div className="pt-2">
                <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">영양성분 표시사항</h3>
                <p className="text-sm text-foreground/80 whitespace-pre-wrap leading-relaxed bg-muted/10 p-3 rounded-lg border border-border/50">
                  {haccp.nutrient_info}
                </p>
              </div>
            ) : null}
          </div>
        </section>
      ) : null}

      <footer className="rounded-xl border border-border bg-card p-5 text-xs text-muted-foreground flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 shadow-sm font-medium">
        <div>
          <p>데이터 연동 출처: 식품안전나라 통합 정보망</p>
          <p className="mt-1">처분 공시 일자: {formatRegisteredDate(item.registered_at)}</p>
        </div>
        <Link 
          href={"https://www.foodsafetykorea.go.kr"} 
          target="_blank" 
          className="inline-flex items-center gap-1 text-primary hover:underline hover:text-primary/95 shrink-0 self-start sm:self-center font-bold"
        >
          공식 식약처 원문 확인
          <ExternalLink className="size-3.5" />
        </Link>
      </footer>
    </main>
  )
}

function DetailSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-border bg-card p-6 shadow-sm">
      <h2 className="text-base font-extrabold text-primary border-b border-border/60 pb-2 mb-3">{title}</h2>
      <dl className="space-y-2.5">{children}</dl>
    </section>
  )
}
