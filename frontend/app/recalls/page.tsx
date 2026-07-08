"use client"

import { useCallback, useEffect, useState } from "react"
import Link from "next/link"
import { EmptyState } from "@/components/common/empty-state"
import { ErrorState } from "@/components/common/error-state"
import { SkeletonCard } from "@/components/common/skeleton-card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from "@/components/ui/table"
import { fetchRecallList } from "@/lib/api/recalls-client"
import type { RecallItem } from "@/types/api"
import { AlertTriangle, ArrowRight, RefreshCw } from "lucide-react"

const PAGE_SIZE_ALL_FIRST = 10
const PAGE_SIZE_ALL_MORE = 20
const PAGE_SIZE_GRADE = 20
const MAX_ITEMS_ALL = 100

export default function RecallsListPage() {
  const [grade, setGrade] = useState<1 | 2 | 3 | "all">("all")
  const [page, setPage] = useState(1)
  const [items, setItems] = useState<RecallItem[]>([])
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const isGradeFilter = grade !== "all"

  const load = useCallback(
    async (nextPage: number, append: boolean) => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetchRecallList({
          food_category: "전체",
          grade: grade === "all" ? undefined : grade,
          page: nextPage,
          size: isGradeFilter
            ? PAGE_SIZE_GRADE
            : nextPage <= 1
              ? PAGE_SIZE_ALL_FIRST
              : PAGE_SIZE_ALL_MORE,
        })
        setTotal(res.total)
        setPage(res.page)
        setItems((prev) => (append ? [...prev, ...res.items] : res.items))
      } catch (err: any) {
        setError("공공 데이터베이스와 연동하지 못했습니다. 잠시 후 다시 시도해 주세요.")
      } finally {
        setLoading(false)
      }
    },
    [grade, isGradeFilter],
  )

  useEffect(() => {
    void load(1, false)
  }, [load])

  const hasMore = !isGradeFilter && items.length < Math.min(total, MAX_ITEMS_ALL)

  const getGradeBadge = (gradeVal: string | number | null | undefined) => {
    const gradeStr = String(gradeVal ?? "")
    const clean = gradeStr.replace(/[^0-9]/g, "")
    if (clean === "1") {
      return (
        <Badge variant="outline" className="border-red-500 bg-red-500/10 text-red-500 font-semibold gap-1 py-0.5">
          <span className="h-1.5 w-1.5 rounded-full bg-red-500 animate-pulse" />
          1등급 (위해성 최상)
        </Badge>
      )
    } else if (clean === "2") {
      return (
        <Badge variant="outline" className="border-amber-500 bg-amber-500/10 text-amber-500 font-semibold gap-1 py-0.5">
          <span className="h-1.5 w-1.5 rounded-full bg-amber-500" />
          2등급 (위해성 상)
        </Badge>
      )
    } else {
      return (
        <Badge variant="outline" className="border-blue-500 bg-blue-500/10 text-blue-500 font-semibold gap-1 py-0.5">
          <span className="h-1.5 w-1.5 rounded-full bg-blue-500" />
          3등급 (위해성 중)
        </Badge>
      )
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <header className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-border/80 pb-6">
        <div className="space-y-2">
          <div className="flex items-center gap-2 text-primary font-semibold text-xs uppercase tracking-wider">
            <AlertTriangle className="size-4 text-primary" />
            Public API Realtime Database
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-foreground">
            회수·판매중지 위해식품 리포트
          </h1>
          <p className="text-sm text-muted-foreground max-w-2xl">
            식품의약품안전처 및 공공 연동 포트를 기반으로 회수 등급별 실시간 위해 정보를 테이블 그리드로 제공합니다. 
            상세 조회 시 실시간 원재료 위해성 조회가 동시 분석됩니다.
          </p>
        </div>
        
        <Button
          variant="outline"
          onClick={() => void load(1, false)}
          disabled={loading}
          className="gap-2 shrink-0 cursor-pointer self-start md:self-end"
        >
          <RefreshCw className={`size-4 ${loading ? "animate-spin" : ""}`} />
          새로고침
        </Button>
      </header>

      {/* McKinsey Style Filter Section */}
      <section className="flex flex-col gap-3 rounded-xl border border-border bg-card p-5 shadow-sm">
        <div className="flex flex-col gap-2">
          <span className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">회수 등급 필터</span>
          <div className="flex flex-wrap gap-2">
            {(["all", 1, 2, 3] as const).map((g) => (
              <Button
                key={String(g)}
                type="button"
                size="sm"
                variant={grade === g ? "default" : "outline"}
                onClick={() => setGrade(g)}
                className="font-medium cursor-pointer"
              >
                {g === "all" ? "전체 목록" : `${g}등급 위해식품`}
              </Button>
            ))}
          </div>
        </div>
      </section>

      <div className="flex items-center justify-between text-sm font-medium text-muted-foreground">
        <span>총 {total}건의 위해 이력 검색됨 {isGradeFilter ? `(조건: ${grade}등급)` : "(조건: 전체)"}</span>
      </div>

      {loading && !items.length ? (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : error ? (
        <ErrorState description={error} onRetry={() => void load(1, false)} />
      ) : !items.length ? (
        <EmptyState
          title="검색된 위해 식품 정보가 없습니다."
          description="현재 백엔드 및 식품안전나라 연동 포트에 새로운 데이터가 없는 상태이거나 API 호출 한계 상태입니다."
        />
      ) : (
        <div className="rounded-xl border border-border bg-card overflow-hidden shadow-sm">
          <Table>
            <TableHeader className="bg-muted/10">
              <TableRow className="border-b border-border/80">
                <TableHead className="w-[180px] font-semibold text-foreground">회수 위해 등급</TableHead>
                <TableHead className="font-semibold text-foreground">제품명</TableHead>
                <TableHead className="w-[200px] font-semibold text-foreground">제조원 (생산처)</TableHead>
                <TableHead className="w-[140px] font-semibold text-foreground text-center">등록일자</TableHead>
                <TableHead className="w-[120px] font-semibold text-foreground text-right">상세 리포트</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {items.map((item) => (
                <TableRow 
                  key={item.id} 
                  className="border-b border-border/50 hover:bg-muted/5 transition-colors"
                >
                  <TableCell className="py-4 font-medium">
                    {getGradeBadge(item.recall_grade)}
                  </TableCell>
                  <TableCell className="py-4">
                    <div className="font-bold text-foreground text-sm">{item.product_name}</div>
                    <div className="text-xs text-muted-foreground line-clamp-1 mt-1">{item.recall_reason}</div>
                  </TableCell>
                  <TableCell className="py-4 text-muted-foreground text-xs font-medium">
                    {item.manufacturer || "정보 미제공"}
                  </TableCell>
                  <TableCell className="py-4 text-center text-xs font-mono text-muted-foreground">
                    {item.registered_at ? item.registered_at.slice(0, 10) : "-"}
                  </TableCell>
                  <TableCell className="py-4 text-right">
                    <Link href={`/recalls/${item.id}`} passHref>
                      <Button variant="ghost" size="sm" className="gap-1 font-semibold text-xs cursor-pointer">
                        분석서
                        <ArrowRight className="size-3" />
                      </Button>
                    </Link>
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
          className="mx-auto w-full max-w-xs shadow-sm font-semibold cursor-pointer"
          disabled={loading}
          onClick={() => void load(page + 1, true)}
        >
          {loading ? "데이터 로드 중..." : "위해 이력 더 보기"}
        </Button>
      ) : null}
    </main>
  )
}
