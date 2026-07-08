"use client"

import { useEffect, useRef, useState } from "react"
import { ScanFace, Sparkles } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { adminFetch } from "@/lib/admin/auth"

type Status = "idle" | "loading" | "success" | "error"

type Prediction = {
  label: string
  confidence: number
}

type RecognitionResult = {
  filename: string
  label: string
  confidence: number
  candidates: Prediction[]
}

const ALLOWED_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif", ".webp", ".bmp"]

function hasAllowedExtension(filename: string): boolean {
  const lower = filename.toLowerCase()
  return ALLOWED_EXTENSIONS.some((ext) => lower.endsWith(ext))
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`
}

export function FaceRecognizeForm() {
  const [file, setFile] = useState<File | null>(null)
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [status, setStatus] = useState<Status>("idle")
  const [message, setMessage] = useState("")
  const [result, setResult] = useState<RecognitionResult | null>(null)
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

  async function handleRecognize() {
    if (!file) return
    setStatus("loading")
    setMessage("")
    setResult(null)

    try {
      const form = new FormData()
      form.append("file", file)

      const res = await adminFetch("/admin/vision/recognize", {
        method: "POST",
        body: form,
      })
      const data = (await res.json()) as RecognitionResult & { detail?: string }

      if (res.ok) {
        setStatus("success")
        setResult(data)
      } else {
        setStatus("error")
        setMessage(data.detail ?? "인식에 실패했습니다.")
      }
    } catch {
      setStatus("error")
      setMessage("네트워크 오류가 발생했습니다.")
    }
  }

  return (
    <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
      <CardHeader>
        <CardTitle>얼굴 인식</CardTitle>
        <CardDescription>사람 얼굴 이미지를 올리면 학습된 인물 중 누구인지 예측합니다.</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="space-y-1.5">
          <Label htmlFor="face-recognize-file">얼굴 이미지</Label>
          <input
            id="face-recognize-file"
            ref={inputRef}
            type="file"
            accept="image/*"
            onChange={(e) => handleFileChange(e.target.files?.[0] ?? null)}
            className="flex h-11 w-full cursor-pointer rounded-md border border-border bg-input px-3 py-2 text-sm text-foreground file:mr-3 file:rounded-md file:border-0 file:bg-primary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-primary-foreground"
          />
        </div>

        {previewUrl && (
          <div className="overflow-hidden rounded-lg border border-border/60">
            <img src={previewUrl} alt="인식 대상 미리보기" className="max-h-64 w-full object-contain bg-muted/20" />
          </div>
        )}

        {message && <p className="text-sm font-medium text-destructive">{message}</p>}

        {result && (
          <div className="space-y-4 rounded-lg border border-border/60 bg-muted/20 p-4">
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-primary" />
              <span className="text-sm text-muted-foreground">예측 결과</span>
              <span className="ml-auto text-2xl font-black tracking-tight text-foreground">{result.label}</span>
            </div>
            <div className="space-y-2">
              {result.candidates.map((candidate, index) => (
                <div key={`${candidate.label}-${index}`} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className={index === 0 ? "font-semibold text-foreground" : "text-muted-foreground"}>
                      {candidate.label}
                    </span>
                    <span className="tabular-nums text-muted-foreground">{formatPercent(candidate.confidence)}</span>
                  </div>
                  <div className="h-2 overflow-hidden rounded-full bg-muted">
                    <div
                      className={index === 0 ? "h-full rounded-full bg-primary" : "h-full rounded-full bg-primary/40"}
                      style={{ width: `${Math.max(2, candidate.confidence * 100)}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        <Button
          type="button"
          disabled={!file || status === "loading"}
          onClick={() => void handleRecognize()}
          className="w-full gap-2"
        >
          {status === "loading" ? (
            <>
              <ScanFace className="h-4 w-4 animate-pulse" />
              인식 중...
            </>
          ) : (
            <>
              <ScanFace className="h-4 w-4" />
              얼굴 인식하기
            </>
          )}
        </Button>
      </CardContent>
    </Card>
  )
}
