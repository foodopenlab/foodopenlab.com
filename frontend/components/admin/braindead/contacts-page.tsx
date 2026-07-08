"use client"

import { useCallback, useEffect, useRef, useState } from "react"
import { BookUser, Upload, UserPlus, X } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { cn } from "@/lib/utils"
import { adminFetch } from "@/lib/admin/auth"

type Contact = {
  id: number
  name: string | null
  email: string | null
  phone: string | null
  company: string | null
  note: string | null
}

function isCsvFile(file: File): boolean {
  const lower = file.name.toLowerCase()
  if (!lower.endsWith(".csv")) return false
  if (!file.type || file.type === "application/octet-stream") return true
  return file.type === "text/csv" || file.type === "application/csv" || file.type === "application/vnd.ms-excel"
}

function UploadDialogContent({ onSuccess }: { onSuccess: () => void }) {
  const inputRef = useRef<HTMLInputElement>(null)
  const dragDepth = useRef(0)
  const [file, setFile] = useState<File | null>(null)
  const [isDragging, setIsDragging] = useState(false)
  const [isUploading, setIsUploading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [savedCount, setSavedCount] = useState<number | null>(null)

  const applyFile = (next: File | undefined) => {
    if (!next) return
    if (!isCsvFile(next)) {
      setError("CSV 파일만 업로드할 수 있습니다.")
      setFile(null)
      return
    }
    setError(null)
    setSavedCount(null)
    setFile(next)
  }

  const upload = useCallback(async () => {
    if (!file) return
    setIsUploading(true)
    setError(null)
    setSavedCount(null)
    try {
      const form = new FormData()
      form.append("file", file)
      const res = await adminFetch("/admin/braindead/contacts/upload", {
        method: "POST",
        body: form,
        signal: AbortSignal.timeout(60_000),
      })
      if (!res.ok) {
        const body = await res.json().catch(() => ({}))
        throw new Error(body?.detail ?? `오류 (${res.status})`)
      }
      const data = await res.json() as { count?: number }
      setSavedCount(data.count ?? 0)
      setFile(null)
      if (inputRef.current) inputRef.current.value = ""
      onSuccess()
    } catch (e) {
      setError(e instanceof Error ? e.message : "업로드 중 오류가 발생했습니다.")
    } finally {
      setIsUploading(false)
    }
  }, [file, onSuccess])

  return (
    <div className="space-y-4">
      <Label htmlFor="contacts-csv-input" className="sr-only">CSV 파일 선택</Label>
      <input
        ref={inputRef}
        id="contacts-csv-input"
        type="file"
        accept=".csv,text/csv"
        className="sr-only"
        onChange={(e) => { applyFile(e.target.files?.[0]); e.target.value = "" }}
      />

      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); inputRef.current?.click() } }}
        onClick={() => inputRef.current?.click()}
        onDrop={(e) => { e.preventDefault(); dragDepth.current = 0; setIsDragging(false); applyFile(e.dataTransfer.files?.[0]) }}
        onDragOver={(e) => { e.preventDefault(); e.dataTransfer.dropEffect = "copy" }}
        onDragEnter={(e) => { e.preventDefault(); dragDepth.current += 1; setIsDragging(true) }}
        onDragLeave={(e) => { e.preventDefault(); dragDepth.current -= 1; if (dragDepth.current <= 0) { dragDepth.current = 0; setIsDragging(false) } }}
        className={cn(
          "flex min-h-[80px] cursor-pointer items-center gap-4 rounded-lg border-2 border-dashed px-5 py-4 outline-none transition-colors focus-visible:ring-2 focus-visible:ring-ring",
          isDragging ? "border-primary bg-primary/15" : "border-border/70 bg-background/40 hover:border-primary/50",
        )}
      >
        <div className="flex size-10 items-center justify-center rounded-md bg-background shadow-sm">
          <Upload className="size-5 text-muted-foreground" aria-hidden />
        </div>
        <div className="space-y-0.5 text-left">
          <p className="text-sm font-semibold">파일을 끌어다 놓거나 클릭하여 선택</p>
          <p className="text-xs text-muted-foreground">name / email / phone / company / note 컬럼 (한글도 가능)</p>
        </div>
      </div>

      {file && (
        <div className="flex items-center justify-between rounded-lg border border-border/60 bg-muted/40 px-4 py-3">
          <p className="truncate text-sm font-medium">{file.name}</p>
          <Button type="button" variant="ghost" size="icon-sm" onClick={() => setFile(null)} aria-label="파일 제거">
            <X className="size-4" />
          </Button>
        </div>
      )}

      {error && (
        <Alert variant="destructive">
          <AlertTitle>업로드 실패</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {savedCount !== null && (
        <Alert>
          <AlertTitle>저장 완료</AlertTitle>
          <AlertDescription>
            {savedCount}개 연락처가 저장되었습니다. 다음 파일을 바로 업로드할 수 있습니다.
          </AlertDescription>
        </Alert>
      )}

      <Button type="button" className="w-full" disabled={!file || isUploading} onClick={() => void upload()}>
        {isUploading ? "업로드 중..." : "업로드"}
      </Button>
    </div>
  )
}

export function BraindeadContactsPage() {
  const [count, setCount] = useState<number | null>(null)
  const [loading, setLoading] = useState(true)

  const fetchContacts = useCallback(async () => {
    setLoading(true)
    try {
      const res = await adminFetch("/admin/braindead/contacts")
      if (res.ok) {
        const data = await res.json() as Contact[]
        setCount(data.length)
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { void fetchContacts() }, [fetchContacts])

  const handleSuccess = useCallback(() => {
    void fetchContacts()
  }, [fetchContacts])

  return (
    <div className="container mx-auto max-w-5xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">BRAINDEAD · ADDRESS BOOK</p>
        <h1 className="text-4xl font-black tracking-tight sm:text-5xl">주소록</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          CSV를 업로드해 연락처를 등록하고 관리합니다.
        </p>
      </div>

      <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="flex items-center gap-2">
            <BookUser className="size-5 shrink-0 text-primary" aria-hidden />
            연락처 목록
          </CardTitle>
          <Dialog>
            <DialogTrigger asChild>
              <Button size="sm" className="gap-1.5">
                <UserPlus className="size-4" aria-hidden />
                등록
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-md">
              <DialogHeader>
                <DialogTitle>주소록 등록</DialogTitle>
                <DialogDescription>CSV 파일을 업로드하면 연락처가 추가됩니다.</DialogDescription>
              </DialogHeader>
              <UploadDialogContent onSuccess={handleSuccess} />
            </DialogContent>
          </Dialog>
        </CardHeader>

        <CardContent>
          {loading ? (
            <p className="py-12 text-center text-sm text-muted-foreground">불러오는 중...</p>
          ) : count === 0 ? (
            <p className="py-12 text-center text-sm text-muted-foreground">
              등록된 연락처가 없습니다. 상단 등록 버튼으로 CSV를 업로드하세요.
            </p>
          ) : (
            <p className="py-12 text-center text-2xl font-bold text-foreground">
              {count?.toLocaleString()}
              <span className="ml-2 text-base font-normal text-muted-foreground">개 연락처 저장됨</span>
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
