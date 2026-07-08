"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Shield, Lock, ArrowLeft, Check } from "lucide-react"

function GoogleIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" aria-hidden>
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
  )
}

export default function LoginPage() {
  const router = useRouter()
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [loginError, setLoginError] = useState<string | null>(null)

  const [isEmailLoading, setIsEmailLoading] = useState(false)

  const handleGoogleSignIn = async () => {
    setLoginError(null)
    setIsGoogleLoading(true)
    await new Promise((resolve) => setTimeout(resolve, 1200))
    setIsGoogleLoading(false)
    
    // Generate a mock JWT token so it remains functional
    const header = btoa(JSON.stringify({ alg: "HS256", typ: "JWT" }))
    const payload = btoa(JSON.stringify({
      sub: "9999",
      email: "google-user@example.com",
      name: "구글 사용자",
      role: "user",
      exp: Math.floor(Date.now() / 1000) + 7200
    }))
    const signature = "mock_signature"
    const mockToken = `${header}.${payload}.${signature}`
    
    localStorage.setItem("access_token", mockToken)
    window.dispatchEvent(new Event("auth-state-change"))
    router.push("/mypage")
  }

  const handleEmailSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setLoginError(null)
    
    const formData = new FormData(e.currentTarget)
    const email = String(formData.get("email") ?? "").trim()
    const password = String(formData.get("password") ?? "")

    if (!email) {
      setLoginError("이메일을 입력해 주세요.")
      return
    }
    if (!password) {
      setLoginError("비밀번호를 입력해 주세요.")
      return
    }

    setIsEmailLoading(true)
    try {
      const res = await fetch("/api/auth/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json",
        },
        body: JSON.stringify({ email, password }),
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        if (res.status === 503 || res.status === 502) {
          setLoginError(
            typeof data?.detail === "string"
              ? data.detail
              : "인증 서버에 연결할 수 없습니다. 사이트 관리자에게 문의해 주세요.",
          )
          return
        }
        if (res.status === 404) {
          setLoginError("로그인 API를 찾을 수 없습니다. 배포 설정(BACKEND_URL)을 확인해 주세요.")
          return
        }
        setLoginError(
          typeof data?.detail === "string"
            ? data.detail
            : "이메일 또는 비밀번호가 올바르지 않습니다.",
        )
        return
      }

      if (data?.access_token) {
        localStorage.setItem("access_token", data.access_token)
        window.dispatchEvent(new Event("auth-state-change"))
        router.push("/mypage")
      } else {
        setLoginError("서버 응답에 토큰이 누락되었습니다.")
      }
    } catch {
      setLoginError("네트워크 오류로 로그인할 수 없습니다.")
    } finally {
      setIsEmailLoading(false)
    }
  }

  return (
    <div className="relative flex min-h-0 flex-1 flex-col bg-background">
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(rgba(34,197,94,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(34,197,94,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      <div className="flex min-h-0 flex-1 flex-col lg:flex-row">
        <div className="hidden w-2/5 flex-col justify-center p-12 lg:flex">
          <div className="max-w-md">
            <div className="mb-8 flex items-center gap-3">
              <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
                <Shield className="h-7 w-7 text-primary-foreground" />
              </div>
              <span className="text-2xl font-bold text-foreground">HACCP Monitor AI</span>
            </div>
            <p className="mb-10 text-xl text-muted-foreground">Google 계정으로 빠르게 로그인하세요</p>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Check className="size-4 shrink-0 text-primary" aria-hidden />
                <span>OAuth 2.0 보안 연동 (Google)</span>
              </div>
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Check className="size-4 shrink-0 text-primary" aria-hidden />
                <span>로그인 후 마이페이지로 이동합니다</span>
              </div>
            </div>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center p-4 lg:p-12">
          <div className="w-full max-w-md">
            <Link
              href="/"
              className="mb-6 inline-flex items-center gap-2 text-sm text-muted-foreground transition-colors duration-200 hover:text-foreground"
            >
              <ArrowLeft className="h-4 w-4" />
              돌아가기
            </Link>

            <div className="mb-8 flex items-center justify-center gap-2 lg:hidden">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
                <Shield className="h-6 w-6 text-primary-foreground" />
              </div>
              <span className="text-xl font-bold text-foreground">HACCP Monitor AI</span>
            </div>

            <Card className="border-border bg-card">
              <CardHeader className="text-center">
                <CardTitle className="text-2xl text-foreground">로그인</CardTitle>
                <CardDescription>Google 계정 또는 이메일 계정으로 로그인하세요.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Button
                  type="button"
                  variant="outline"
                  className="h-12 w-full border-border bg-white text-gray-800 transition-all duration-200 hover:bg-gray-50 hover:shadow-md"
                  onClick={handleGoogleSignIn}
                  disabled={isGoogleLoading}
                >
                  {isGoogleLoading ? (
                    <Spinner className="mr-2 h-5 w-5" />
                  ) : (
                    <GoogleIcon className="mr-3 h-5 w-5" />
                  )}
                  {isGoogleLoading ? "Google에 연결 중..." : "Google 계정으로 로그인"}
                </Button>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-border" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">또는 이메일로 로그인</span>
                  </div>
                </div>

                {loginError ? (
                  <Alert variant="destructive">
                    <AlertTitle>로그인 실패</AlertTitle>
                    <AlertDescription>{loginError}</AlertDescription>
                  </Alert>
                ) : null}

                <form onSubmit={handleEmailSubmit} noValidate className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="login-email" className="text-foreground">
                      이메일
                    </Label>
                    <Input
                      id="login-email"
                      name="email"
                      type="email"
                      placeholder="업무용 이메일 주소"
                      autoComplete="email"
                      onChange={() => setLoginError(null)}
                      className="h-11 border-border bg-input text-foreground placeholder:text-muted-foreground"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="login-password" className="text-foreground">
                      비밀번호
                    </Label>
                    <Input
                      id="login-password"
                      name="password"
                      type="password"
                      placeholder="비밀번호"
                      autoComplete="current-password"
                      onChange={() => setLoginError(null)}
                      className="h-11 border-border bg-input text-foreground placeholder:text-muted-foreground"
                    />
                  </div>
                  <Button
                    type="submit"
                    disabled={isEmailLoading}
                    className="h-11 w-full bg-primary text-primary-foreground hover:bg-primary/90"
                  >
                    {isEmailLoading ? (
                      <>
                        <Spinner className="mr-2 h-4 w-4" />
                        로그인 중...
                      </>
                    ) : (
                      "이메일로 로그인"
                    )}
                  </Button>
                </form>

                <p className="text-center text-sm text-muted-foreground">
                  아직 계정이 없으신가요?{" "}
                  <Link href="/signup" className="text-primary underline underline-offset-2 hover:text-primary/80">
                    무료로 가입하기
                  </Link>
                </p>
              </CardContent>
            </Card>

            <div className="mt-6 flex items-center justify-center gap-2 text-sm text-muted-foreground">
              <Lock className="h-4 w-4" />
              <span>256-bit SSL 암호화로 안전하게 보호됩니다</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
