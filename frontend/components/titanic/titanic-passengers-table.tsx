"use client"

import { useEffect, useMemo, useState } from "react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

type PassengerRow = Record<string, unknown>

type PassengerPage = {
  page: number
  size: number
  total: number
  items: PassengerRow[]
}

function buildPagination(totalPages: number, currentPage: number): Array<number | "ellipsis"> {
  if (totalPages <= 1) return [1]
  const items: Array<number | "ellipsis"> = []
  const add = (v: number | "ellipsis") => {
    if (items.length && items[items.length - 1] === v) return
    items.push(v)
  }

  add(1)
  const start = Math.max(2, currentPage - 2)
  const end = Math.min(totalPages - 1, currentPage + 2)
  if (start > 2) add("ellipsis")
  for (let p = start; p <= end; p += 1) add(p)
  if (end < totalPages - 1) add("ellipsis")
  add(totalPages)
  return items
}

export function TitanicPassengersTable() {
  const [page, setPage] = useState(1)
  const [size] = useState(50)
  const [data, setData] = useState<PassengerPage | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const backendOrigin =
    (process.env.NEXT_PUBLIC_API_URL || process.env.NEXT_PUBLIC_BACKEND_URL || "").replace(/\/$/, "") ||
    "http://127.0.0.1:8000"

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetch(`${backendOrigin}/titanic/reader/passengers?page=${page}&size=${size}`)
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text().catch(() => "")
          throw new Error(`(${res.status}) ${text || "요청에 실패했습니다."}`)
        }
        return (await res.json()) as PassengerPage
      })
      .then((json) => {
        if (cancelled) return
        setData(json)
      })
      .catch((e) => {
        if (cancelled) return
        setError(e instanceof Error ? e.message : "불러오기 중 오류가 발생했습니다.")
        setData(null)
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [backendOrigin, page, size])

  const headers = useMemo(() => {
    const first = data?.items?.[0]
    if (!first) return []
    const keys = Object.keys(first)
    const preferred = [
      "passenger_id",
      "survived",
      "pclass",
      "name",
      "gender",
      "age",
      "sib_sp",
      "parch",
      "ticket",
      "fare",
      "cabin",
      "embarked",
    ]
    const ordered = preferred.filter((k) => keys.includes(k))
    for (const k of keys) {
      if (!ordered.includes(k)) ordered.push(k)
    }
    return ordered
  }, [data])

  const totalPages = Math.max(1, Math.ceil((data?.total ?? 0) / size))
  const paginationItems = useMemo(() => buildPagination(totalPages, page), [page, totalPages])

  return (
    <div className="space-y-3">
      {error ? (
        <Alert variant="destructive">
          <AlertTitle>불러올 수 없습니다</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      ) : null}

      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="text-sm text-muted-foreground">
          {loading ? "불러오는 중..." : `총 ${data?.total?.toLocaleString?.() ?? 0}개`}
        </div>
        <div className="flex flex-wrap items-center justify-end gap-1">
          {paginationItems.map((it, idx) =>
            it === "ellipsis" ? (
              <span key={`e-${idx}`} className="px-2 text-xs text-muted-foreground">
                …
              </span>
            ) : (
              <Button
                key={it}
                type="button"
                variant={it === page ? "default" : "secondary"}
                size="sm"
                className="h-8 px-2"
                onClick={() => setPage(it)}
                disabled={loading}
              >
                {it}
              </Button>
            ),
          )}
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-border/60">
        <table className="w-full min-w-[1200px] border-collapse text-sm">
          <thead className="bg-muted/40">
            <tr>
              {headers.map((h) => (
                <th key={h} className="whitespace-nowrap border-b border-border/50 px-4 py-2.5 text-left font-semibold">
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {(data?.items ?? []).map((row, idx) => (
              <tr key={`${page}-${idx}`} className={cn("odd:bg-background/30", loading && "opacity-60")}>
                {headers.map((h) => (
                  <td key={h} className="whitespace-nowrap border-b border-border/30 px-4 py-2.5">
                    {String((row as Record<string, unknown>)[h] ?? "")}
                  </td>
                ))}
              </tr>
            ))}
            {!loading && (data?.items?.length ?? 0) === 0 ? (
              <tr>
                <td className="px-4 py-6 text-sm text-muted-foreground" colSpan={headers.length || 1}>
                  데이터가 없습니다. 먼저 CSV를 업로드해 주세요.
                </td>
              </tr>
            ) : null}
          </tbody>
        </table>
      </div>
    </div>
  )
}

