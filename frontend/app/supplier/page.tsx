"use client"

import { useState } from "react"
import { Search } from "lucide-react"
import { ErrorState } from "@/components/common/error-state"
import { SkeletonCard } from "@/components/common/skeleton-card"
import { SupplierRiskCardView } from "@/components/supplier/supplier-risk-card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { fetchSupplierRiskCard } from "@/lib/api/supplier-client"
import type { SupplierRiskCard } from "@/lib/types/supplier"

export default function SupplierPage() {
  const [searchText, setSearchText] = useState("")
  const [keyword, setKeyword] = useState("")
  const [data, setData] = useState<SupplierRiskCard | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const submitSearch = async () => {
    const name = searchText.trim()
    if (!name) return
    setKeyword(name)
    setLoading(true)
    setError(null)
    setData(null)
    try {
      const card = await fetchSupplierRiskCard(name)
      setData(card)
    } catch (e) {
      setError(e instanceof Error ? e.message : "조회에 실패했습니다.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-3xl flex-1 flex-col gap-6 px-4 py-8 md:py-10">
      <header className="space-y-2">
        <p className="text-sm font-medium text-primary">회수·행정처분·인허가(데모) 집계</p>
        <h1 className="text-2xl font-semibold tracking-tight text-foreground md:text-3xl">납품사 조회</h1>
        <p className="text-sm text-muted-foreground">
          업체명으로 캐시 DB를 검색해 리스크 등급과 최근 이력을 확인합니다. (예: 한빛, 록신)
        </p>
      </header>

      <section className="rounded-2xl border border-border/70 bg-card/50 p-4">
        <div className="flex gap-2">
          <Input
            placeholder="납품사·제조사명 검색"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") void submitSearch()
            }}
            aria-label="업체명"
          />
          <Button type="button" onClick={() => void submitSearch()} disabled={loading || !searchText.trim()}>
            <Search className="mr-1 h-4 w-4" aria-hidden />
            조회
          </Button>
        </div>
      </section>

      {loading && (
        <div className="space-y-3">
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {error && !loading && <ErrorState description={error} onRetry={() => void submitSearch()} />}

      {data && !loading && !error && keyword && <SupplierRiskCardView data={data} />}
    </main>
  )
}
