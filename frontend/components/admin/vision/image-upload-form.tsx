"use client"

import { useEffect, useRef, useState } from "react"
import { ImageUp, UploadCloud } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { adminFetch } from "@/lib/admin/auth"

type Status = "idle" | "loading" | "success" | "error"

type UploadResult = {
  id: string
  filename: string
  content_type: string
  size: number
}

const ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]

function hasAllowedExtension(filename: string): boolean {
  const lower = filename.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

export function VisionImageUploadForm() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")
  const [result, setResult] = useState<UploadResult | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (!file) {
      setPreviewUrl(null)
      return
    }
    const url = URL.createObjectURL(file)
    setPreviewUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [file])

  function handleFileChange(selected: File | null) {
    setResult(null)
    setMessage("")
    setStatus("idle")

    if (!selected) {
      setFile(null)
      return
    }
    if (!hasAllowedExtension(selected.name)) {
      setFile(null)
      setStatus("error")
      setMessage(`지원하지 않는 이미지 확장자입니다. (허용: ${ALLOWED_EXTENSIONS.join(", ")})`)
      return
    }
    setFile(selected)
  }

  async function handleUpload() {
    if (!file) return
    setStatus("loading")
    setMessage("")

    try {
      const form = new FormData()
      form.append("file", file)

      const res = await adminFetch("/admin/vision/images", {
        method: "POST",
        body: form,
      })
      const data = (await res.json()) as UploadResult & { detail?: string }

      if (res.ok) {
        setStatus("success")
        setMessage("업로드가 완료되었습니다.")
        setResult(data)
        setFile(null)
        if (inputRef.current) inputRef.current.value = ""
      } else {
        setStatus("error")
        setMessage(data.detail ?? "업로드에 실패했습니다.")
      }
    } catch {
      setStatus("error")
      setMessage("네트워크 오류가 발생했습니다.")
    }
  }

  return (
    <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
      <CardHeader>
        <CardTitle>이미지 업로드</CardTitle>
        <CardDescription>png, jpg, jpeg, gif, webp, bmp 확장자의 이미지를 업로드할 수 있습니다.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-1.5">
          <Label htmlFor="vision-image-file">이미지 파일</Label>
          <input
            id="vision-image-file"
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
            className="flex h-11 w-full cursor-pointer rounded-md border border-border bg-input px-3 py-2 text-sm text-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary-foreground"
          />
        </div>

        {previewUrl && (
          <div className="overflow-hidden rounded-lg border border-border/60">
            <img src={previewUrl} alt="업로드 미리보기" className="max-h-64 w-full object-contain bg-muted/20" />
          </div>
        )}

        {message && (
          <p
            className={
              status === "success"
                ? "text-sm font-medium text-green-600 dark:text-green-400"
                : "text-sm font-medium text-destructive"
            }
          >
            {message}
          </p>
        )}

        {result && (
          <div className="rounded-lg border border-border/60 bg-muted/20 p-3 text-xs text-muted-foreground">
            <p>파일명: {result.filename}</p>
            <p>크기: {formatBytes(result.size)}</p>
            <p>ID: {result.id}</p>
          </div>
        )}

        <Button
          type="button"
          disabled={!file || status === "loading"}
          onClick={() => void handleUpload()}
          className="w-full gap-2"
        >
          {status === "loading" ? (
            <>
              <UploadCloud className="h-4 w-4 animate-pulse" />
              업로드 중...
            </>
          ) : (
            <>
              <ImageUp className="h-4 w-4" />
              업로드
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
