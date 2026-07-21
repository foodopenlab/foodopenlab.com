"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { socialLoginUrl } from "@/lib/oauth-url"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Spinner } from "@/components/ui/spinner"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Shield, Lock, ArrowLeft, Check } from "lucide-react"
import { KakaoIcon, NaverIcon } from "@/components/icons/social-icons"

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
  const [isGoogleLoading, setIsGoogleLoading] = useState(false)
  const [isKakaoLoading, setIsKakaoLoading] = useState(false)
  const [isNaverLoading, setIsNaverLoading] = useState(false)
  const [loginError, setLoginError] = useState<string | null>(null)

  // 소셜 로그인 콜백 실패(백엔드가 /login?oauth_error=1 로 되돌림) 시 안내.
  useEffect(() => {
    if (new URLSearchParams(window.location.search).get("oauth_error")) {
      setLoginError("소셜 로그인에 실패했습니다. 다시 시도해 주세요.")
      window.history.replaceState(null, "", "/login")
    }
  }, [])

  // 소셜 로그인 — 백엔드 OAuth 시작 URL로 top-level 이동(Authorization Code 플로우).
  const handleGoogleSignIn = () => {
    setIsGoogleLoading(true)
    window.location.href = socialLoginUrl("google")
  }
  const handleKakaoSignIn = () => {
    setIsKakaoLoading(true)
    window.location.href = socialLoginUrl("kakao")
  }
  const handleNaverSignIn = () => {
    setIsNaverLoading(true)
    window.location.href = socialLoginUrl("naver")
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
            <p className="mb-10 text-xl text-muted-foreground">소셜 계정으로 빠르게 로그인하세요</p>
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm text-muted-foreground">
                <Check className="size-4 shrink-0 text-primary" aria-hidden />
                <span>OAuth 2.0 보안 연동 (카카오·네이버·Google)</span>
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
                <CardDescription>소셜 계정으로 로그인하세요.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {loginError ? (
                  <Alert variant="destructive">
                    <AlertTitle>로그인 실패</AlertTitle>
                    <AlertDescription>{loginError}</AlertDescription>
                  </Alert>
                ) : null}

                <div className="space-y-3">
                  <Button
                    type="button"
                    variant="outline"
                    className="h-12 w-full border-transparent bg-[#FEE500] text-[#191919] transition-all duration-200 hover:bg-[#FDD835] hover:shadow-md"
                    onClick={handleKakaoSignIn}
                    disabled={isKakaoLoading}
                  >
                    {isKakaoLoading ? (
                      <Spinner className="mr-2 h-5 w-5" />
                    ) : (
                      <KakaoIcon className="mr-3 h-5 w-5" />
                    )}
                    {isKakaoLoading ? "카카오에 연결 중..." : "카카오로 로그인"}
                  </Button>

                  <Button
                    type="button"
                    variant="outline"
                    className="h-12 w-full border-transparent bg-[#03C75A] text-white transition-all duration-200 hover:bg-[#02b350] hover:shadow-md"
                    onClick={handleNaverSignIn}
                    disabled={isNaverLoading}
                  >
                    {isNaverLoading ? (
                      <Spinner className="mr-2 h-5 w-5" />
                    ) : (
                      <NaverIcon className="mr-3 h-5 w-5" />
                    )}
                    {isNaverLoading ? "네이버에 연결 중..." : "네이버로 로그인"}
                  </Button>

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
                </div>

                <p className="text-center text-sm text-muted-foreground">
                  아직 계정이 없으신가요?{" "}
                  <Link href="/signup" className="text-primary underline underline-offset-2 hover:text-primary/80">
                    소셜 계정으로 가입하기
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
