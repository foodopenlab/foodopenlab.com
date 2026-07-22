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

    // 통합 토큰의 role로 목적지 분기 — admin이면 관리자 화면으로.
    let isAdmin = false
    try {
      const p = JSON.parse(
        decodeURIComponent(
          atob(accessToken.split(".")[1].replace(/-/g, "+").replace(/_/g, "/"))
            .split("")
            .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
            .join("")
        )
      )
      isAdmin = p.role === "admin" || (Array.isArray(p.roles) && p.roles.includes("admin"))
    } catch {
      isAdmin = false
    }
    router.replace(isAdmin ? "/admin" : "/mypage")
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
