"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Spinner } from "@/components/ui/spinner"

export default function DashboardPage() {
  const router = useRouter()

  useEffect(() => {
    router.replace("/mypage")
  }, [router])

  return (
    <div className="flex min-h-[50vh] flex-1 flex-col items-center justify-center gap-4 bg-background">
      <Spinner className="h-8 w-8 text-primary" />
      <p className="text-sm text-muted-foreground animate-pulse">마이페이지로 이동 중...</p>
    </div>
  )
}

