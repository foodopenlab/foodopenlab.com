"use client"

import { useCallback, useMemo, useRef, useState } from "react"
import { FileSpreadsheet, Upload, X } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { titanicUploadUrl } from "@/lib/api-path"

function isCsvFile(file: File): boolean {
  const lower = file.name.toLowerCase()
  if (!lower.endsWith(".csv")) return false
  if (!file.type || file.type === "application/octet-stream") return true
  return (
    file.type === "text/csv" ||
    file.type === "application/csv" ||
    file.type === "application/vnd.ms-excel"
  )
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 B"
  const k = 1024
  const sizes = ["B", "KB", "MB", "GB"]
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(1))} ${sizes[i]}`
}

type CsvPreviewRow = Record<string, string>

function parseCsvLine(line: string): string[] {
  const out: string[] = []
  let cur = ""
  let inQuotes = false
  for (let i = 0; i < line.length; i += 1) {
    const ch = line[i]
    if (ch === '"') {
      if (inQuotes && line[i + 1] === '"') {
        cur += '"'
        i += 1
      } else {
        inQuotes = !inQuotes
      }
      continue
    }
    if (ch === "," && !inQuotes) {
      out.push(cur)
      cur = ""
      continue
    }
    cur += ch
  }
  out.push(cur)
  return out
}

async function parseCsvForPreview(file: File): Promise<{ headers: string[]; rows: CsvPreviewRow[] }> {
  const text = await file.text()
  const lines = text.replace(/^\uFEFF/, "").split(/\r?\n/).filter(Boolean)
  if (lines.length === 0) return { headers: [], rows: [] }
  const headers = parseCsvLine(lines[0]).map((h) => h.trim())
  const rows: CsvPreviewRow[] = []
  for (let i = 1; i < lines.length; i += 1) {
    const cols = parseCsvLine(lines[i])
    const row: CsvPreviewRow = {}
    for (let j = 0; j < headers.length; j += 1) {
      row[headers[j]] = (cols[j] ?? "").trim()
    }
    // Sex -> gender 미리보기에서도 동일 매핑
    if (row.Sex && !row.gender) {
      row.gender = row.Sex
    }
    rows.push(row)
  }
  return { headers, rows }
}

export function CsvUploadSection() {
  const inputRef = useRef<HTMLInputElement>(null)
  const dragDepth = useRef(0)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [uploadResult, setUploadResult] = useState<{ count: number } | null>(null)
  const [previewHeaders, setPreviewHeaders] = useState<string[]>([])
  const [previewRows, setPreviewRows] = useState<CsvPreviewRow[]>([])
  const [previewPage, setPreviewPage] = useState(0)

  const applyFile = useCallback((next: File | undefined) => {
    if (!next) return
    if (!isCsvFile(next)) {
      setError("CSV 파일만 업로드할 수 있습니다. (.csv 확장자)")
      setFile(null)
      setPreviewHeaders([])
      setPreviewRows([])
      setPreviewPage(0)
      return
    }
    setError(null)
    setFile(next)
    setUploadResult(null)
    setPreviewHeaders([])
    setPreviewRows([])
    setPreviewPage(0)
    void parseCsvForPreview(next)
      .then(({ headers, rows }) => {
        setPreviewHeaders(headers)
        setPreviewRows(rows)
      })
      .catch(() => {
        setPreviewHeaders([])
        setPreviewRows([])
      })
  }, [])

  const onInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    applyFile(e.target.files?.[0])
    e.target.value = ""
  }

  const onDrop = (e: React.DragEvent) => {
    e.preventDefault()
    dragDepth.current = 0
    setIsDragging(false)
    applyFile(e.dataTransfer.files?.[0])
  }

  const onDragOver = (e: React.DragEvent) => {
    e.preventDefault()
    e.dataTransfer.dropEffect = "copy"
  }

  const clearFile = () => {
    setFile(null)
    setError(null)
    setUploadResult(null)
    setPreviewHeaders([])
    setPreviewRows([])
    setPreviewPage(0)
  }

  const upload = useCallback(async () => {
    if (!file) return
    setIsUploading(true)
    setError(null)
    setUploadResult(null)
    try {
      const form = new FormData()
      form.append("file", file)
      const res = await fetch(titanicUploadUrl(), {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(120_000),
      })
      if (!res.ok) {
        const rawText = await res.text().catch(() => "")
        const body = (() => {
          try {
            return rawText ? JSON.parse(rawText) : null
          } catch {
            return null
          }
        })()
        const detail =
          typeof body?.detail === "string"
            ? body.detail
            : rawText
              ? rawText.slice(0, 300)
              : "업로드에 실패했습니다. 잠시 후 다시 시도해 주세요."
        throw new Error(`(${res.status}) ${detail}`)
      }
      const data = (await res.json()) as { count?: number; saved?: number }
      const count = typeof data.count === "number" ? data.count : typeof data.saved === "number" ? data.saved : 0
      setUploadResult({ count })
    } catch (e) {
      const message = e instanceof Error ? e.message : "업로드 중 오류가 발생했습니다."
      if (message.includes("Failed to fetch") || message.includes("aborted") || message.includes("timeout")) {
        setError(
          "업로드 시간이 초과되었거나 백엔드(8000)에 연결할 수 없습니다. backend에서 python main.py 실행 후 다시 시도하세요.",
        )
      } else {
        setError(message)
      }
    } finally {
      setIsUploading(false)
    }
  }, [file])

  const rowsPerPage = 50
  const previewTotalPages = Math.max(1, Math.ceil(previewRows.length / rowsPerPage))
  const pagedRows = useMemo(() => {
    const start = previewPage * rowsPerPage
    return previewRows.slice(start, start + rowsPerPage)
  }, [previewPage, previewRows])

  const paginationItems = useMemo(() => {
    const total = previewTotalPages
    const current = previewPage + 1
    if (total <= 1) return [1]

    const items: Array<number | "ellipsis"> = []
    const add = (v: number | "ellipsis") => {
      if (items.length && items[items.length - 1] === v) return
      items.push(v)
    }

    add(1)
    const start = Math.max(2, current - 2)
    const end = Math.min(total - 1, current + 2)
    if (start > 2) add("ellipsis")
    for (let p = start; p <= end; p += 1) add(p)
    if (end < total - 1) add("ellipsis")
    if (total > 1) add(total)
    return items
  }, [previewPage, previewTotalPages])

  return (
    <Card className="w-full max-w-6xl border-border/50 bg-card/80 text-card-foreground shadow-xl backdrop-blur-md">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileSpreadsheet className="size-5 shrink-0 text-primary" aria-hidden />
          CSV 업로드
        </CardTitle>
        <CardDescription>
          타이타닉 데이터용 CSV를 선택하거나 여기로 끌어다 놓으세요. UTF-8 인코딩을 권장합니다.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <Label htmlFor="titanic-csv-input" className="sr-only">
          CSV 파일 선택
        </Label>
        <input
          ref={inputRef}
          id="titanic-csv-input"
          type="file"
          accept=".csv,text/csv"
          className="sr-only"
          onChange={onInputChange}
        />
        <div
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === "Enter" || e.key === " ") {
              e.preventDefault()
              inputRef.current?.click()
            }
          }}
          onClick={() => inputRef.current?.click()}
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragEnter={(e) => {
            e.preventDefault()
            dragDepth.current += 1
            setIsDragging(true)
          }}
          onDragLeave={(e) => {
            e.preventDefault()
            dragDepth.current -= 1
            if (dragDepth.current <= 0) {
              dragDepth.current = 0
              setIsDragging(false)
            }
          }}
          className={cn(
            "flex min-h-[88px] cursor-pointer items-center justify-between gap-4 rounded-lg border-2 border-dashed px-5 py-4 transition-colors outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
            isDragging
              ? "border-primary bg-primary/15"
              : "border-border/70 bg-background/40 hover:border-primary/50 hover:bg-background/55",
          )}
        >
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex size-10 items-center justify-center rounded-md bg-background shadow-sm",
                isDragging && "text-primary",
              )}
            >
              <Upload className="size-5 text-muted-foreground" aria-hidden />
            </div>
            <div className="space-y-0.5 text-left">
              <p className="text-base font-semibold text-foreground">파일을 끌어다 놓거나 클릭하여 선택</p>
              <p className="text-sm text-muted-foreground">.csv · 업로드 전/후 아래에서 미리보기를 확인할 수 있습니다</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button type="button" variant="secondary" size="sm" onClick={() => inputRef.current?.click()}>
              파일 찾기
            </Button>
            <Button
              type="button"
              variant="default"
              size="sm"
              disabled={!file || isUploading}
              onClick={(e) => {
                e.stopPropagation()
                void upload()
              }}
            >
              {isUploading ? "업로드 중..." : "업로드"}
            </Button>
          </div>
        </div>

        {error ? (
          <Alert variant="destructive">
            <AlertTitle>{error.includes("CSV") ? "선택할 수 없습니다" : "업로드 실패"}</AlertTitle>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        ) : null}

        {uploadResult ? (
          <Alert>
            <AlertTitle>업로드 완료</AlertTitle>
            <AlertDescription>{uploadResult.count.toLocaleString()}개 행을 서버가 수신했습니다.</AlertDescription>
          </Alert>
        ) : null}

        {file ? (
          <div className="flex items-center justify-between gap-3 rounded-lg border border-border/60 bg-muted/40 px-4 py-3">
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-muted-foreground">{formatFileSize(file.size)}</p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="shrink-0 text-muted-foreground hover:text-destructive"
              onClick={(e) => {
                e.stopPropagation()
                clearFile()
              }}
              aria-label="선택한 파일 제거"
            >
              <X className="size-4" />
            </Button>
          </div>
        ) : null}

        {previewRows.length ? (
          <div className="space-y-2">
            <div className="flex items-center justify-between gap-3">
              <p className="text-base font-semibold text-foreground">미리보기</p>
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
                      variant={it === previewPage + 1 ? "default" : "secondary"}
                      size="sm"
                      className="h-8 px-2"
                      onClick={() => setPreviewPage(it - 1)}
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
                    {previewHeaders.map((h) => (
                      <th
                        key={h}
                        className="whitespace-nowrap border-b border-border/50 px-4 py-2.5 text-left font-semibold"
                      >
                        {h === "Sex" ? "Sex (gender)" : h}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {pagedRows.map((row, idx) => (
                    <tr key={`${previewPage}-${idx}`} className="odd:bg-background/30">
                      {previewHeaders.map((h) => (
                        <td key={h} className="whitespace-nowrap border-b border-border/30 px-4 py-2.5">
                          {h === "Sex" ? row.gender || row.Sex || "" : row[h] || ""}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="text-xs text-muted-foreground">
              화면에는 50개씩 표시합니다.
            </p>
          </div>
        ) : null}
      </CardContent>
      <CardFooter className="flex flex-wrap gap-2 border-t border-border/50 pt-6">
        <p className="w-full text-xs text-muted-foreground">
          업로드 시 서버에서 CSV를 파싱하고, Sex 컬럼은 gender로 변환됩니다.
        </p>
      </CardFooter>
    </Card>
  )
}
