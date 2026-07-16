"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { ShieldCheck, Eye, EyeOff } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Spinner } from "@/components/ui/spinner"
import { isAdminLoggedIn, setAdminDisplayName, setAdminToken } from "@/lib/admin/auth"

export default function AdminLoginPage() {
  const router = useRouter()
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isAdminLoggedIn()) router.replace("/admin")
  }, [router])

  const submit = async () => {
    setError(null)
    setLoading(true)
    try {
      const res = await fetch("/api/admin/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), password }),
      })
      const data = (await res.json().catch(() => ({}))) as {
        access_token?: string
        admin_name?: string
        detail?: string
      }
      if (!res.ok) {
        if (res.status === 404) {
          setError(
            "백엔드 API를 찾을 수 없습니다. com.auditor(uvicorn 8000) 또는 Docker backend 컨테이너가 실행 중인지 확인하세요.",
          )
          return
        }
        if (res.status === 503 && typeof data.detail === "string") {
          setError(data.detail)
          return
        }
        setError(
          typeof data.detail === "string"
            ? data.detail
            : res.status === 401
              ? "이메일 또는 비밀번호가 올바르지 않습니다. com.auditor/.env 비밀번호를 바꿨다면 seed_admin 스크립트를 다시 실행했는지 확인하세요."
              : `로그인 실패 (HTTP ${res.status})`,
        )
        return
      }
      if (!data.access_token) {
        setError("로그인 응답이 올바르지 않습니다.")
        return
      }
      setAdminToken(data.access_token)
      if (data.admin_name) setAdminDisplayName(data.admin_name)
      router.push("/admin")
    } catch {
      setError(
        "백엔드에 연결할 수 없습니다. 프론트(localhost:3000)와 백엔드(8000)가 모두 실행 중인지 확인하세요.",
      )
    } finally {
      setLoading(false)
    }
  }

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") void submit()
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4">
      <div className="w-full max-w-md rounded-xl border border-border bg-card p-8 shadow-lg">
        <div className="mb-6 flex flex-col items-center text-center">
          <ShieldCheck className="mb-2 size-12 text-primary" aria-hidden />
          <h1 className="text-xl font-semibold text-foreground">HACCP Monitor</h1>
          <p className="text-sm text-muted-foreground">관리자 로그인</p>
        </div>
        <div className="space-y-4" onKeyDown={onKeyDown}>
          <div className="space-y-2">
            <Label htmlFor="admin-email">이메일</Label>
            <Input
              id="admin-email"
              type="email"
              autoComplete="username"
              placeholder="관리자 이메일"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={loading}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="admin-password">비밀번호</Label>
            <div className="relative">
              <Input
                id="admin-password"
                type={showPw ? "text" : "password"}
                autoComplete="current-password"
                placeholder="비밀번호"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="pr-10"
              />
              <button
                type="button"
                className="absolute right-2 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                onClick={() => setShowPw((v) => !v)}
                aria-label={showPw ? "비밀번호 숨기기" : "비밀번호 표시"}
              >
                {showPw ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
              </button>
            </div>
          </div>
          <Button type="button" className="w-full" disabled={loading} onClick={() => void submit()}>
            {loading ? (
              <>
                <Spinner className="mr-2 size-4" />
                로그인 중…
              </>
            ) : (
              "로그인"
            )}
          </Button>
        </div>
        {error ? <p className="mt-4 text-center text-sm text-destructive">{error}</p> : null}
      </div>
    </div>
  )
}
