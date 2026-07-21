"use client"

import { Suspense, useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { ShieldCheck } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Spinner } from "@/components/ui/spinner"
import { isAdminLoggedIn } from "@/lib/admin/auth"

// OAuth state 쿠키가 백엔드 도메인에 설정돼야 하므로 백엔드 절대 URL로 top-level 이동한다.
function adminGoogleLoginUrl(): string {
  const base = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "")
  return `${base}/admin/auth/google/login`
}

const ERROR_MESSAGES: Record<string, string> = {
  forbidden: "어드민 권한이 없는 구글 계정입니다.",
  state: "인증 요청이 만료되었습니다. 다시 시도해 주세요.",
  config: "어드민 구글 로그인 설정이 완료되지 않았습니다. 관리자에게 문의하세요.",
  oauth: "구글 로그인에 실패했습니다. 다시 시도해 주세요.",
}

function AdminLoginContent() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(false)

  const errorCode = searchParams.get("error")
  const error = errorCode ? (ERROR_MESSAGES[errorCode] ?? "로그인에 실패했습니다.") : null

  useEffect(() => {
    if (isAdminLoggedIn()) router.replace("/admin")
  }, [router])

  const signInWithGoogle = () => {
    setLoading(true)
    window.location.href = adminGoogleLoginUrl()
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 shadow-lg">
        <div className="mb-6 flex flex-col items-center text-center">
          <ShieldCheck className="mb-2 size-12 text-primary" aria-hidden />
          <h1 className="text-xl font-semibold text-foreground">HACCP Monitor</h1>
          <p className="text-sm text-muted-foreground">관리자 로그인</p>
        </div>

        <Button
          type="button"
          variant="outline"
          className="h-12 w-full border-border bg-white text-gray-800 transition-all duration-200 hover:bg-gray-50 hover:shadow-md"
          disabled={loading}
          onClick={signInWithGoogle}
        >
          {loading ? (
            <Spinner className="mr-2 size-5" />
          ) : (
            <svg className="mr-3 size-5" viewBox="0 0 24 24" aria-hidden>
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
          )}
          {loading ? "연결 중…" : "Google 계정으로 로그인"}
        </Button>

        <p className="mt-4 text-center text-xs text-muted-foreground">
          허용된 관리자 구글 계정만 접근할 수 있습니다.
        </p>

        {error ? <p className="mt-4 text-center text-sm text-destructive">{error}</p> : null}
      </div>
    </div>
  )
}

export default function AdminLoginPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-screen items-center justify-center bg-background">
          <Spinner className="size-6" />
        </div>
      }
    >
      <AdminLoginContent />
    </Suspense>
  )
}
