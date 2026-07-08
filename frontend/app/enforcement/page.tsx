"use client"

import { useCallback, useEffect, useMemo, useState } from "react"
import { Search, ShieldAlert, RefreshCw } from "lucide-react"
import { EmptyState } from "@/components/common/empty-state"
import { ErrorState } from "@/components/common/error-state"
import { SkeletonCard } from "@/components/common/skeleton-card"
import { LicensePanel } from "@/components/enforcement/license-panel"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { fetchEnforcementList } from "@/lib/api/enforcement-client"
import type { EnforcementItem } from "@/types/api"
import { cn, formatRegisteredDate } from "@/lib/utils"

type ProcessFilter = "전체" | "영업정지" | "영업취소" | "과징금" | "시정명령" | "기타"

const INITIAL_SIZE = 10
const MAX_ITEMS = 50
const LOAD_MORE_SIZE = 15
const PROCESS_FILTERS: ProcessFilter[] = ["전체", "영업정지", "영업취소", "과징금", "시정명령", "기타"]

const cleanViolation = (violation: string) => {
  if (!violation) return ""
  // 1. Remove (YYYYMMDD) prefix
  let text = violation.replace(/^\(\d{8}\)\s*/, "")
  // 2. Remove YYYY. MM. DD. HH:MM경 (or variations) prefix if it exists
  text = text.replace(/^\d{4}\.\s*\d{1,2}\.\s*\d{1,2}\.\s*(?:\d{1,2}:\d{2}(?:\s*경)?)?\s*/, "")
  return text
}

const formatViolation = (violation: string) => {
  const cleaned = cleanViolation(violation)
  return cleaned
    .replace(/\s+(\()/g, "\n(")
    .replace(/\s+(\[)/g, "\n[")
    .replace(/\s+-\s+/g, "\n- ")
}

export default function EnforcementPage() {
  const [processType, setProcessType] = useState<ProcessFilter>("전체")
  const [searchText, setSearchText] = useState("")
  const [keyword, setKeyword] = useState("")
  const [page, setPage] = useState(1)
  const [items, setItems] = useState<EnforcementItem[]>([])
  const [total, setTotal] = useState(0)
  const [emptyLabel, setEmptyLabel] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [enrichHint, setEnrichHint] = useState(false)
  const [listMax, setListMax] = useState(MAX_ITEMS)

  const loadEnforcements = useCallback(
    async (nextPage: number, append: boolean) => {
      setLoading(true)
      setError(null)
      try {
        const size = nextPage <= 1 ? INITIAL_SIZE : LOAD_MORE_SIZE
        const result = await fetchEnforcementList({
          process_type: processType === "전체" ? undefined : processType,
          business_name: keyword || undefined,
          page: nextPage,
          size,
        })
        
        // Map any field mismatch from backend if needed
        const mappedItems: EnforcementItem[] = result.items.map((x: any) => ({
          id: x.id,
          business_name: x.business_name,
          industry: x.industry || x.induty_desc || "기타",
          disposition_date: x.disposition_date || x.process_date,
          disposition_start: x.disposition_start,
          disposition_type: x.disposition_type || x.process_type,
          violation: x.violation || x.violation_content,
          address: x.address || "정보 미제공",
          representative: x.representative || "정보 미제공",
          disposition_detail: x.disposition_detail || "정보 미제공",
          agency: x.agency || "식품의약품안전처",
          serial_no: x.serial_no || "",
          category: x.category || "행정처분",
          service_id: x.service_id || "I0470"
        }))

        setItems((prev) => (append ? [...prev, ...mappedItems] : mappedItems))
        setTotal(result.total)
        setPage(result.page)
        setEmptyLabel(result.empty_label ?? null)
        setListMax(result.list_max ?? MAX_ITEMS)
        setEnrichHint(!keyword && result.total < INITIAL_SIZE)
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : "행정처분 정보를 데이터베이스로부터 조회하지 못했습니다."
        setError(
          message.includes("Failed to fetch")
            ? "백엔드(FastAPI 8000)에 연결할 수 없습니다. com.auditor에서 python main.py 를 실행한 뒤 새로고침하세요."
            : message,
        )
      } finally {
        setLoading(false)
      }
    },
    [processType, keyword],
  )

  useEffect(() => {
    void loadEnforcements(1, false)
  }, [loadEnforcements])

  const latestProcessDate = useMemo(
    () => (items[0]?.disposition_date ? formatRegisteredDate(items[0].disposition_date) : "-"),
    [items],
  )
  const displayCap = Math.min(total, listMax)
  const hasMore = items.length < displayCap

  const submitSearch = () => {
    setKeyword(searchText.trim())
  }

  const clearSearch = () => {
    setSearchText("")
    setKeyword("")
  }

  const showNotFound = Boolean(keyword) && total === 0 && emptyLabel === "사실없음"

  const getDispositionBadge = (dispType: string) => {
    if (dispType.includes("정지")) {
      return (
        <Badge variant="outline" className="border-red-500 bg-red-500/10 text-red-500 font-semibold py-0.5">
          {dispType}
        </Badge>
      )
    } else if (dispType.includes("취소")) {
      return (
        <Badge variant="outline" className="border-rose-700 bg-rose-700/10 text-rose-600 font-extrabold py-0.5 animate-pulse">
          {dispType}
        </Badge>
      )
    } else if (dispType.includes("과징금")) {
      return (
        <Badge variant="outline" className="border-amber-500 bg-amber-500/10 text-amber-500 font-semibold py-0.5">
          {dispType}
        </Badge>
      )
    } else {
      return (
        <Badge variant="outline" className="border-slate-500 bg-slate-500/10 text-slate-400 font-semibold py-0.5">
          {dispType}
        </Badge>
      )
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/80 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-xs uppercase tracking-wider">
            <ShieldAlert className="size-4 text-primary" />
            Public API Realtime Database
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            식품 영업소 행정처분 이력 리포트
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            식품안전나라 공공 API 연동 및 DB 캐시로부터 취합된 기업체 행정제재 이력 리스트입니다.
            최근 처분확정일: <span className="font-mono text-foreground font-semibold">{latestProcessDate}</span>
          </p>
        </div>
        
        <Button
          variant="outline"
          onClick={() => void loadEnforcements(1, false)}
          disabled={loading}
          className="gap-2 shrink-0 cursor-pointer self-start md:self-end"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} />
          새로고침
        </Button>
      </header>

      {/* Filter and Search Section */}
      <div className="grid gap-4 md:grid-cols-3">
        <section className="md:col-span-2 rounded-xl border border-border bg-card p-5 shadow-sm space-y-4">
          <div className="flex flex-col gap-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">처분대상 업체 검색</span>
            <div className="flex gap-2">
              <Input
                value={searchText}
                onChange={(event) => setSearchText(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter") submitSearch()
                }}
                placeholder="업체명으로 검색 (예: 한빛)"
                className="h-10 font-medium"
              />
              <Button type="button" className="h-10 cursor-pointer" onClick={submitSearch}>
                <Search className="mr-2 h-4 w-4" />
                검색
              </Button>
              {keyword ? (
                <Button type="button" variant="outline" className="h-10 cursor-pointer" onClick={clearSearch}>
                  초기화
                </Button>
              ) : null}
            </div>
            {keyword ? <p className="text-xs text-primary font-semibold">검색 조건: 「{keyword}」 부분 일치</p> : null}
          </div>
        </section>

        <section className="md:col-span-1 rounded-xl border border-border bg-card p-5 shadow-sm">
          <div className="flex flex-col gap-2">
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">처분유형 필터</span>
            <div className="flex flex-wrap gap-1.5">
              {PROCESS_FILTERS.map((value) => (
                <Button
                  key={value}
                  type="button"
                  size="sm"
                  variant={processType === value ? "default" : "outline"}
                  className="text-xs font-semibold cursor-pointer py-1 h-8"
                  onClick={() => setProcessType(value)}
                >
                  {value}
                </Button>
              ))}
            </div>
          </div>
        </section>
      </div>

      <div className="flex items-center justify-between text-sm font-medium text-muted-foreground">
        <span>
          조회 결과: {items.length}개 항목 표시 (총 {total}건 매칭됨)
        </span>
      </div>

      {enrichHint ? (
        <p className="rounded-lg border border-border bg-amber-500/10 border-amber-500/20 px-4 py-3 text-xs text-amber-500 font-semibold leading-relaxed">
          DB에 저장된 행정처분 건수가 적습니다(총 {total}건). 백엔드 스케줄러가 매일 09:40·17:40(KST)에 식품안전나라 API에서 추가 수집합니다.
        </p>
      ) : null}

      <div className={cn("grid gap-6", keyword ? "md:grid-cols-3" : "")}>
        <div className={cn(keyword && "md:col-span-2")}>
          {loading && !items.length ? (
            <div className="space-y-3">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : error ? (
            <ErrorState description={error} onRetry={() => void loadEnforcements(1, false)} />
          ) : showNotFound ? (
            <EmptyState title="사실없음" description="입력한 업체명과 일치하는 행정처분 이력이 데이터베이스에 등록되어 있지 않습니다." />
          ) : !items.length ? (
            <EmptyState
              title="조건에 맞는 행정처분이 없습니다."
              description="처분유형을 바꾸거나 다른 업체명으로 검색해 보세요."
            />
          ) : (
            <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
              <Table>
                <TableHeader className="bg-muted/10">
                  <TableRow className="border-b border-border/80">
                    <TableHead className="w-[120px] font-semibold text-foreground text-center">처분일자</TableHead>
                    <TableHead className="font-semibold text-foreground">업체정보</TableHead>
                    <TableHead className="w-[150px] font-semibold text-foreground">제재조치</TableHead>
                    <TableHead className="w-[300px] font-semibold text-foreground">위반 사유</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {items.map((item) => (
                    <TableRow 
                      key={item.id} 
                      className="border-b border-border/50 hover:bg-muted/5 transition-colors"
                    >
                      <TableCell className="py-4 text-center text-xs font-mono text-muted-foreground align-top">
                        {item.disposition_date ? item.disposition_date.slice(0, 10) : "-"}
                      </TableCell>
                      <TableCell className="py-4 align-top">
                        <div className="font-bold text-foreground text-sm">{item.business_name}</div>
                        <div className="text-[11px] text-muted-foreground mt-1">
                          대표: {item.representative} | 업종: {item.industry}
                        </div>
                        <div className="text-[10px] text-muted-foreground mt-0.5 truncate max-w-[280px]">
                          {item.address}
                        </div>
                      </TableCell>
                      <TableCell className="py-4 align-top">
                        <div className="mb-1">{getDispositionBadge(item.disposition_type)}</div>
                        <div className="text-[10px] font-semibold text-muted-foreground mt-0.5 leading-tight">
                          {item.disposition_detail}
                        </div>
                      </TableCell>
                      <TableCell className="py-4 text-xs font-medium text-foreground leading-relaxed w-[300px] align-top">
                        <div className="font-semibold text-rose-500 whitespace-pre-wrap max-h-[80px] overflow-y-auto pr-1">
                          {formatViolation(item.violation)}
                        </div>
                        <div className="text-[10px] text-muted-foreground mt-1">단속: {item.agency}</div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}

          {hasMore ? (
            <Button
              type="button"
              variant="outline"
              className="mx-auto mt-4 w-full max-w-xs shadow-sm font-semibold cursor-pointer"
              disabled={loading}
              onClick={() => void loadEnforcements(page + 1, true)}
            >
              {loading ? "데이터 로드 중..." : `더 보기 (${items.length}/${displayCap}건)`}
            </Button>
          ) : null}
        </div>

        {keyword && !showNotFound ? (
          <div className="md:col-span-1">
            <LicensePanel businessName={keyword} />
          </div>
        ) : null}
      </div>
    </main>
  )
}
