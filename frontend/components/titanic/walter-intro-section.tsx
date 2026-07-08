"use client"

import { useEffect, useState } from "react"
import { UserRound } from "lucide-react"

import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

type WalterIntro = {
  id: number
  name: string
}

const REPO_SUFFIX = "가 레포지토리에 다녀옴"

function splitWalterIntro(name: string): { title: string; message: string } {
  if (name.endsWith(REPO_SUFFIX)) {
    return {
      title: name.slice(0, -REPO_SUFFIX.length),
      message: name,
    }
  }
  return { title: name, message: name }
}

export function WalterIntroSection() {
  const [data, setData] = useState<WalterIntro | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)

    fetch("/api/lesson/titanic/walter/myself")
      .then(async (res) => {
        if (!res.ok) {
          const text = await res.text().catch(() => "")
          throw new Error(`(${res.status}) ${text || "요청에 실패했습니다."}`)
        }
        return (await res.json()) as WalterIntro
      })
      .then((json) => {
        if (cancelled) return
        setData(json)
      })
      .catch((e) => {
        if (cancelled) return
        const message = e instanceof Error ? e.message : "불러오기 중 오류가 발생했습니다."
        setError(
          message.includes("Failed to fetch")
            ? "백엔드에 연결할 수 없습니다. uvicorn(8000)과 Next(3000)가 실행 중인지 확인하세요."
            : message,
        )
        setData(null)
      })
      .finally(() => {
        if (cancelled) return
        setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [])

  if (loading) {
    return <p className="text-sm text-muted-foreground">월터 정보를 불러오는 중…</p>
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertTitle>불러오기 실패</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    )
  }

  if (!data) {
    return null
  }

  const { title, message } = splitWalterIntro(data.name)

  return (
    <Card className="border-border/60 bg-background/40">
      <CardHeader className="flex flex-row items-center gap-3 space-y-0">
        <div className="flex size-12 items-center justify-center rounded-full bg-primary/15 text-primary">
          <UserRound className="size-6" aria-hidden />
        </div>
        <div>
          <CardTitle className="text-xl">{title}</CardTitle>
          <CardDescription>승무원 ID {data.id}</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-base leading-relaxed text-foreground">{message}</p>
      </CardContent>
    </Card>
  )
}
