"use client"

import { useState } from "react"
import { useMyPageAuth } from "@/hooks/use-mypage-auth"
import { PasswordStrengthCheck } from "@/components/mypage/password-strength-check"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Eye, EyeOff, Lock, AlertTriangle, ShieldCheck } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { Skeleton } from "@/components/ui/skeleton"

export default function PasswordChangePage() {
  const { token, isLoading: isAuthLoading } = useMyPageAuth()
  const { toast } = useToast()

  // Form Fields
  const [currentPassword, setCurrentPassword] = useState("")
  const [newPassword, setNewPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")

  // Toggles for showing/hiding password
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)

  // API loading & error states
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<{ currentPassword?: string; newPassword?: string; confirmPassword?: string }>({})

  // Security validators
  const hasLength = newPassword.length >= 8
  const hasSpecial = /[!@#$%^&*(),.?":{}|<>_\[\]\\\/~`\-+=]/.test(newPassword)
  const isMatching = newPassword === confirmPassword && confirmPassword.length > 0

  const handleResetForm = () => {
    setCurrentPassword("")
    setNewPassword("")
    setConfirmPassword("")
    setError(null)
    setFieldErrors({})
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setFieldErrors({})

    // Client side checks
    let localErrors: typeof fieldErrors = {}
    if (!currentPassword) {
      localErrors.currentPassword = "현재 비밀번호를 입력해 주세요."
    }
    if (!newPassword) {
      localErrors.newPassword = "새 비밀번호를 입력해 주세요."
    } else if (!hasLength || !hasSpecial) {
      localErrors.newPassword = "새 비밀번호 요구사항을 충족해야 합니다."
    }
    if (newPassword && newPassword === currentPassword) {
      localErrors.newPassword = "새 비밀번호는 현재 비밀번호와 다르게 설정해야 합니다."
    }
    if (!confirmPassword) {
      localErrors.confirmPassword = "새 비밀번호 확인을 입력해 주세요."
    } else if (newPassword !== confirmPassword) {
      localErrors.confirmPassword = "새 비밀번호가 일치하지 않습니다."
    }

    if (Object.keys(localErrors).length > 0) {
      setFieldErrors(localErrors)
      return
    }

    setIsLoading(true)
    try {
      const res = await fetch("/api/mypage/password", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword,
          confirm_password: confirmPassword,
        }),
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        if (res.status === 400) {
          // Current password incorrect
          setFieldErrors({ currentPassword: data?.detail || "현재 비밀번호가 올바르지 않습니다." })
        } else {
          setError(data?.detail || "비밀번호 변경에 실패했습니다. 입력값을 확인해 주세요.")
        }
        return
      }

      toast({
        title: "비밀번호 변경 완료",
        description: "비밀번호가 성공적으로 업데이트되었습니다.",
      })
      handleResetForm()
    } catch {
      setError("네트워크 오류가 발생했습니다. 잠시 후 다시 시도해 주세요.")
    } finally {
      setIsLoading(false)
    }
  }

  if (isAuthLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-96 w-full rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-xl">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-foreground">비밀번호 변경</h1>
        <p className="text-sm text-muted-foreground">보안을 위해 비밀번호를 주기적으로 변경하는 것을 권장합니다.</p>
      </div>

      <Card className="border border-border bg-card shadow-sm">
        <CardContent className="p-6">
          {error && (
            <Alert variant="destructive" className="mb-5">
              <AlertTriangle className="h-4 w-4" />
              <AlertTitle>변경 오류</AlertTitle>
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            
            {/* Current Password */}
            <div className="space-y-2">
              <Label htmlFor="current-password">현재 비밀번호</Label>
              <div className="relative">
                <Input
                  id="current-password"
                  type={showCurrent ? "text" : "password"}
                  value={currentPassword}
                  onChange={(e) => {
                    setCurrentPassword(e.target.value)
                    setFieldErrors((prev) => ({ ...prev, currentPassword: undefined }))
                  }}
                  className="pr-10 border-border bg-input"
                  placeholder="현재 비밀번호를 입력하세요"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowCurrent(!showCurrent)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showCurrent ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {fieldErrors.currentPassword && (
                <p className="text-xs text-destructive font-medium">{fieldErrors.currentPassword}</p>
              )}
            </div>

            {/* New Password */}
            <div className="space-y-2">
              <Label htmlFor="new-password">새 비밀번호</Label>
              <div className="relative">
                <Input
                  id="new-password"
                  type={showNew ? "text" : "password"}
                  value={newPassword}
                  onChange={(e) => {
                    setNewPassword(e.target.value)
                    setFieldErrors((prev) => ({ ...prev, newPassword: undefined }))
                  }}
                  className="pr-10 border-border bg-input"
                  placeholder="새 비밀번호를 입력하세요 (8자 이상, 특수문자 포함)"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowNew(!showNew)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showNew ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {fieldErrors.newPassword && (
                <p className="text-xs text-destructive font-medium">{fieldErrors.newPassword}</p>
              )}
              {newPassword.length > 0 && (
                <div className="pt-1">
                  <PasswordStrengthCheck hasLength={hasLength} hasSpecial={hasSpecial} />
                </div>
              )}
            </div>

            {/* Confirm Password */}
            <div className="space-y-2">
              <Label htmlFor="confirm-password">새 비밀번호 확인</Label>
              <div className="relative">
                <Input
                  id="confirm-password"
                  type={showConfirm ? "text" : "password"}
                  value={confirmPassword}
                  onChange={(e) => {
                    setConfirmPassword(e.target.value)
                    setFieldErrors((prev) => ({ ...prev, confirmPassword: undefined }))
                  }}
                  className="pr-10 border-border bg-input"
                  placeholder="새 비밀번호를 한 번 더 입력하세요"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowConfirm(!showConfirm)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                >
                  {showConfirm ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
              </div>
              {fieldErrors.confirmPassword && (
                <p className="text-xs text-destructive font-medium">{fieldErrors.confirmPassword}</p>
              )}
              {confirmPassword.length > 0 && (
                <p className={`text-xs font-semibold flex items-center gap-1.5 ${isMatching ? "text-emerald-500" : "text-destructive"}`}>
                  <ShieldCheck className="h-3.5 w-3.5" />
                  {isMatching ? "새 비밀번호와 일치합니다." : "새 비밀번호가 일치하지 않습니다."}
                </p>
              )}
            </div>

            <div className="pt-4">
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full h-11 bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {isLoading ? (
                  <>
                    <Spinner className="mr-2 h-4 w-4" />
                    변경 처리 중...
                  </>
                ) : (
                  "비밀번호 변경"
                )}
              </Button>
            </div>

          </form>

          {/* Muted Caution warning */}
          <div className="flex items-center gap-2 mt-5 text-[11px] text-muted-foreground justify-center">
            <Lock className="h-3 w-3" />
            <span>비밀번호는 일방향 암호화되어 안전하게 저장되며, 어떠한 직원도 확인할 수 없습니다.</span>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
