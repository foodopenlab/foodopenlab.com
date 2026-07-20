"use client"

import { useState } from "react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Checkbox } from "@/components/ui/checkbox"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Spinner } from "@/components/ui/spinner"
import { Shield, Check, Lock, ArrowLeft } from "lucide-react"
import { KakaoIcon, NaverIcon } from "@/components/icons/social-icons"
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group"
import { apiPath } from "@/lib/api-path"
import { mergeFieldAndClearFormError } from "@/lib/form-feedback"
import { socialLoginUrl } from "@/lib/oauth-url"

const SIGNUP_API_URL = apiPath("auth/signup")

function formatSignupApiError(detail: unknown): string {
  if (typeof detail === "string") return detail
  if (Array.isArray(detail)) {
    return detail
      .map((item) =>
        typeof item === "object" && item !== null && "msg" in item ? String((item as { msg: string }).msg) : JSON.stringify(item),
      )
      .join(", ")
  }
  return "회원가입 요청에 실패했습니다."
}

type SignupRequestBody = {
  email: string
  password: string
  name: string
  agreed: boolean
  role: "expert"
}

type SignupPageState = {
  email: string
  password: string
  name: string
  signUpType: "expert" | "anonymous"
  agreed: boolean
  isGoogleLoading: boolean
  isKakaoLoading: boolean
  isNaverLoading: boolean
  isSubmitting: boolean
  formError: string | null
}

const initialSignupState: SignupPageState = {
  email: "",
  password: "",
  name: "",
  signUpType: "expert",
  agreed: false,
  isGoogleLoading: false,
  isKakaoLoading: false,
  isNaverLoading: false,
  isSubmitting: false,
  formError: null,
}

function parseSignupFormEntries(entries: Record<string, FormDataEntryValue>) {
  const email = String(entries.email ?? "").trim()
  const name = String(entries.name ?? "").trim()
  const password = String(entries.password ?? "")
  const agreed = entries.agreed === "true"
  return { email, name, password, agreed }
}

export default function SignupPage() {
  const router = useRouter()
  const [state, setState] = useState<SignupPageState>(initialSignupState)

  const patchState = (patch: Partial<SignupPageState>) => {
    setState((prev) => ({ ...prev, ...patch }))
  }

  // 소셜 가입/로그인 — 백엔드 OAuth 시작 URL로 top-level 이동(Authorization Code 플로우).
  const handleGoogleSignIn = () => {
    patchState({ isGoogleLoading: true })
    window.location.href = socialLoginUrl("google")
  }
  const handleKakaoSignIn = () => {
    patchState({ isKakaoLoading: true })
    window.location.href = socialLoginUrl("kakao")
  }
  const handleNaverSignIn = () => {
    patchState({ isNaverLoading: true })
    window.location.href = socialLoginUrl("naver")
  }

  const handleSignup = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const formProps = Object.fromEntries(formData.entries())
    const { email, name, password, agreed } = parseSignupFormEntries(formProps)

    patchState({
      email,
      name,
      password,
      agreed,
      formError: null,
    })

    if (!email || email.indexOf("@") < 0) {
      patchState({ formError: "업무용 이메일 주소에 @가 포함된 올바른 형식을 입력해 주세요." })
      return
    }
    if (password.length < 8) {
      patchState({ formError: "비밀번호는 8자 이상 입력해 주세요." })
      return
    }
    if (!name) {
      patchState({ formError: "이름 또는 표시명을 입력해 주세요." })
      return
    }
    if (!agreed) {
      patchState({ formError: "이용약관 및 개인정보처리방침에 동의해 주세요." })
      return
    }

    const signupPayload: SignupRequestBody = {
      email,
      password,
      name,
      agreed,
      role: "expert",
    }

    patchState({ isSubmitting: true })
    try {
      const res = await fetch(SIGNUP_API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(signupPayload),
      })

      const data: unknown = await res.json().catch(() => null)

      if (!res.ok) {
        const detail =
          data !== null && typeof data === "object" && "detail" in data ? (data as { detail: unknown }).detail : null
        patchState({ formError: formatSignupApiError(detail) })
        return
      }

      const accessToken =
        data !== null && typeof data === "object" && "access_token" in data
          ? (data as { access_token: unknown }).access_token
          : null

      if (typeof accessToken !== "string" || !accessToken) {
        patchState({ formError: "가입은 완료되었지만 자동 로그인에 실패했습니다. 로그인 페이지에서 다시 시도해 주세요." })
        return
      }

      localStorage.setItem("access_token", accessToken)
      // 전문가로 승격된 계정만 업종 온보딩으로, 신규 일반회원은 마이페이지로.
      const signedRole =
        data !== null && typeof data === "object" && "role" in data ? (data as { role: unknown }).role : null
      router.push(signedRole === "expert" ? "/mypage/industry" : "/mypage")
    } catch {
      patchState({ formError: "네트워크 오류로 가입 요청을 보낼 수 없습니다. 잠시 후 다시 시도해 주세요." })
    } finally {
      patchState({ isSubmitting: false })
    }
  }

  const { email, password, name, signUpType, agreed, isGoogleLoading, isKakaoLoading, isNaverLoading, isSubmitting, formError } = state

  return (
    <div className="flex min-h-screen bg-background">
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(rgba(34,197,94,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(34,197,94,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />

      <div className="hidden w-2/5 flex-col justify-center p-12 lg:flex">
        <div className="max-w-md">
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-primary">
              <Shield className="h-7 w-7 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold text-foreground">HACCP Monitor AI</span>
          </div>

          <p className="mb-10 text-xl text-muted-foreground">위해식품 모니터링을 AI와 함께</p>

          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20">
                <Check className="h-4 w-4 text-primary" />
              </div>
              <span className="text-foreground">식품안전나라 실시간 연동</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20">
                <Check className="h-4 w-4 text-primary" />
              </div>
              <span className="text-foreground">원료 위험도 자동 평가</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="flex h-6 w-6 items-center justify-center rounded-full bg-primary/20">
                <Check className="h-4 w-4 text-primary" />
              </div>
              <span className="text-foreground">HACCP 관리점 매핑</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex flex-1 items-center justify-center p-4 lg:p-12">
        <div className="w-full max-w-md">
          <Link
            href="/"
            className="mb-6 inline-flex items-center gap-2 text-muted-foreground transition-colors duration-200 hover:text-foreground"
          >
            <ArrowLeft className="h-4 w-4" />
            <span className="text-sm">돌아가기</span>
          </Link>

          <div className="mb-8 flex items-center justify-center gap-2 lg:hidden">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Shield className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">HACCP Monitor AI</span>
          </div>

          <Card className="border-border bg-card">
            <CardHeader className="text-center">
              <CardTitle className="text-2xl text-foreground">계정 만들기</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
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
                  {isKakaoLoading ? "연결 중..." : "카카오로 시작하기"}
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
                  {isNaverLoading ? "연결 중..." : "네이버로 시작하기"}
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
                    <svg className="mr-3 h-5 w-5" viewBox="0 0 24 24" aria-hidden>
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
                  {isGoogleLoading ? "연결 중..." : "Google 계정으로 시작하기"}
                </Button>
              </div>

              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-border" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-card px-2 text-muted-foreground">또는 이메일로 가입</span>
                </div>
              </div>

              {formError ? (
                <Alert variant="destructive">
                  <AlertTitle>입력 확인</AlertTitle>
                  <AlertDescription>{formError}</AlertDescription>
                </Alert>
              ) : null}

              <div className="space-y-4">
                <div className="space-y-3">
                  <Label className="text-foreground">가입 유형</Label>
                  <RadioGroup
                    value={signUpType}
                    onValueChange={(v) => {
                      if (v === "expert" || v === "anonymous") {
                        patchState({ signUpType: v, formError: null })
                      }
                    }}
                    className="grid gap-2 sm:grid-cols-2"
                  >
                    <label className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm hover:bg-muted/40">
                      <RadioGroupItem value="expert" id="type-expert" />
                      <span className="font-semibold text-foreground">전문가회원</span>
                    </label>
                    <label className="flex cursor-pointer items-center gap-2 rounded-md border border-border bg-background px-3 py-2 text-sm hover:bg-muted/40">
                      <RadioGroupItem value="anonymous" id="type-anonymous" />
                      <span className="font-semibold text-foreground">비회원</span>
                    </label>
                  </RadioGroup>
                </div>

                {signUpType === "anonymous" ? (
                  <div className="space-y-4 rounded-xl border border-border/80 bg-muted/20 p-4 text-center">
                    <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <Shield className="h-5 w-5" />
                    </div>
                    <div className="space-y-1">
                      <h3 className="text-sm font-semibold text-foreground">비회원 서비스 이용 안내</h3>
                      <p className="text-xs text-muted-foreground leading-relaxed">
                        비회원은 별도의 회원가입 없이 위해식품 조회, 공공데이터 통계, AI 원료 분석 등 대부분의 핵심 서비스를 자유롭게 이용할 수 있습니다.
                      </p>
                    </div>
                    <Button
                      type="button"
                      asChild
                      className="w-full h-10 text-xs bg-primary text-primary-foreground hover:bg-primary/90 mt-2"
                    >
                      <Link href="/">비회원으로 즉시 시작하기</Link>
                    </Button>
                  </div>
                ) : (
                  <form onSubmit={handleSignup} noValidate className="space-y-4">
                    <input type="hidden" name="agreed" value={agreed ? "true" : "false"} readOnly />

                    <div className="space-y-2">
                      <Input
                        id="signup-email"
                        name="email"
                        type="email"
                        placeholder="업무용 이메일 주소"
                        value={email}
                        onChange={(e) => patchState(mergeFieldAndClearFormError("email", e.target.value))}
                        autoComplete="email"
                        className="h-11 border-border bg-input text-foreground placeholder:text-muted-foreground"
                      />
                      <p className="text-[10px] text-muted-foreground px-1 leading-normal">
                        💡 관리자가 등록한 전문가 화이트리스트 이메일 주소만 가입 승인 처리됩니다.
                      </p>
                    </div>
                    <div className="space-y-2">
                      <Input
                        id="signup-password"
                        name="password"
                        type="password"
                        placeholder="비밀번호 (8자 이상)"
                        value={password}
                        onChange={(e) => patchState(mergeFieldAndClearFormError("password", e.target.value))}
                        autoComplete="new-password"
                        className="h-11 border-border bg-input text-foreground placeholder:text-muted-foreground"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="signup-name" className="text-foreground">
                        이름 또는 표시명
                      </Label>
                      <Input
                        id="signup-name"
                        name="name"
                        type="text"
                        placeholder="예: 홍길동"
                        value={name}
                        onChange={(e) => patchState(mergeFieldAndClearFormError("name", e.target.value))}
                        autoComplete="organization"
                        className="h-11 border-border bg-input text-foreground placeholder:text-muted-foreground"
                      />
                    </div>

                    <div className="flex items-start space-x-2">
                      <Checkbox
                        id="terms"
                        checked={agreed}
                        onCheckedChange={(checked) => {
                          patchState({ agreed: checked === true, formError: null })
                        }}
                        className="mt-0.5 border-border data-[state=checked]:bg-primary data-[state=checked]:border-primary"
                      />
                      <Label htmlFor="terms" className="text-sm leading-relaxed text-muted-foreground">
                        <span className="text-foreground">(필수)</span>{" "}
                        <Link href="/terms" className="text-primary underline underline-offset-2 hover:text-primary/80">
                          이용약관
                        </Link>{" "}
                        및{" "}
                        <Link href="/privacy" className="text-primary underline underline-offset-2 hover:text-primary/80">
                          개인정보처리방침
                        </Link>
                        에 동의합니다
                      </Label>
                    </div>

                    <Button
                      type="submit"
                      disabled={isSubmitting}
                      className="h-11 w-full bg-primary text-primary-foreground hover:bg-primary/90"
                    >
                      {isSubmitting ? (
                        <>
                          <Spinner className="mr-2 h-4 w-4" />
                          가입 처리 중...
                        </>
                      ) : (
                        "무료 계정 만들기"
                      )}
                    </Button>
                  </form>
                )}
              </div>

              <p className="text-center text-sm text-muted-foreground">
                이미 계정이 있으신가요?{" "}
                <Link href="/login" className="text-primary underline underline-offset-2 hover:text-primary/80">
                  로그인하기
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
  )
}
