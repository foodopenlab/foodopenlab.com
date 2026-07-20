"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { Spinner } from "@/components/ui/spinner"

export default function OAuthCallbackPage() {
  const router = useRouter()
  const [error, setError] = useState(false)

  useEffect(() => {
    // 백엔드가 토큰을 URL fragment(#access_token=...&refresh_token=...)로 전달한다.
    const hash = window.location.hash.startsWith("#") ? window.location.hash.slice(1) : window.location.hash
    const params = new URLSearchParams(hash)
    const accessToken = params.get("access_token")
    const refreshToken = params.get("refresh_token")

    if (!accessToken) {
      setError(true)
      const t = setTimeout(() => router.replace("/login?oauth_error=1"), 1500)
      return () => clearTimeout(t)
    }

    localStorage.setItem("access_token", accessToken)
    if (refreshToken) localStorage.setItem("refresh_token", refreshToken)
    // 주소창에서 토큰 제거 후 상태 전파.
    window.history.replaceState(null, "", "/auth/callback")
    window.dispatchEvent(new Event("auth-state-change"))
    router.replace("/mypage")
  }, [router])

  return (
    <div className="flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
      <Spinner className="h-8 w-8" />
      <p className="text-sm text-muted-foreground">
        {error ? "로그인에 실패했습니다. 로그인 페이지로 이동합니다…" : "로그인 처리 중입니다…"}
      </p>
    </div>
  )
}
