"use client"

import { useEffect } from "react"
import { useRouter } from "next/navigation"
import { Spinner } from "@/components/ui/spinner"
import { setAdminToken, setAdminDisplayName, decodeAdminJwtPayload } from "@/lib/admin/auth"

// 백엔드 구글 콜백이 #access_token=... fragment로 어드민 JWT를 전달한다.
export default function AdminAuthCallbackPage() {
  const router = useRouter()

  useEffect(() => {
    const params = new URLSearchParams(window.location.hash.slice(1))
    const token = params.get("access_token")
    if (!token) {
      router.replace("/admin/login?error=oauth")
      return
    }
    setAdminToken(token)
    const payload = decodeAdminJwtPayload(token)
    if (payload?.email) setAdminDisplayName(payload.email)
    // 주소창의 토큰 fragment 제거 후 이동
    window.history.replaceState(null, "", "/admin/auth/callback")
    router.replace("/admin")
  }, [router])

  return (
    <div className="flex min-h-screen items-center justify-center bg-background">
      <div className="flex flex-col items-center gap-3 text-muted-foreground">
        <Spinner className="size-6" />
        <p className="text-sm">로그인 처리 중…</p>
      </div>
    </div>
  )
}
