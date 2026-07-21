"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { useMyPageAuth } from "@/hooks/use-mypage-auth"
import { Button } from "@/components/ui/button"
import { Label } from "@/components/ui/label"
import { Checkbox } from "@/components/ui/checkbox"
import { Card, CardContent } from "@/components/ui/card"
import { AlertTriangle, Lock, Trash2 } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"
import { Skeleton } from "@/components/ui/skeleton"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export default function WithdrawalPage() {
  const { token, isLoading: isAuthLoading, logOut } = useMyPageAuth()
  const router = useRouter()
  const { toast } = useToast()

  const [isChecked, setIsChecked] = useState(false)

  // API states
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [isDialogOpen, setIsDialogOpen] = useState(false)

  const handleWithdrawal = async () => {
    setIsLoading(true)
    setError(null)
    setIsDialogOpen(false)

    try {
      // 소셜 전용 가입이라 비밀번호가 없다 — 인증 토큰만으로 탈퇴한다.
      const res = await fetch("/api/mypage/withdraw", {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        setError(data?.detail || "회원 탈퇴 처리에 실패했습니다.")
        return
      }

      toast({
        title: "회원 탈퇴 완료",
        description: "회원 탈퇴 처리가 정상적으로 완료되었습니다. 잠시 후 홈 화면으로 이동합니다.",
      })

      // Clean up token and redirect
      setTimeout(() => {
        localStorage.removeItem("access_token")
        router.push("/")
        // Force refresh to clear navbar auth state
        router.refresh()
      }, 2000)
    } catch {
      setError("네트워크 문제로 회원 탈퇴에 실패했습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  if (isAuthLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-40" />
        <Skeleton className="h-48 w-full rounded-xl" />
        <Skeleton className="h-32 w-full rounded-xl" />
      </div>
    )
  }

  return (
    <div className="space-y-6 max-w-xl">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-foreground">회원 탈퇴</h1>
        <p className="text-sm text-muted-foreground">더 이상 HACCP Monitor AI 서비스를 이용하지 않으실 경우 탈퇴를 신청할 수 있습니다.</p>
      </div>

      {/* Warning Card */}
      <Card className="border-destructive/30 bg-destructive/5 dark:bg-destructive/10 shadow-sm overflow-hidden">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center gap-2.5 text-destructive font-bold text-sm">
            <AlertTriangle className="h-5 w-5 shrink-0 animate-pulse" />
            <span>회원 탈퇴 시 유의사항 (필독)</span>
          </div>
          
          <div className="space-y-2 text-xs leading-relaxed text-muted-foreground">
            <p>회원 탈퇴 시 아래의 보존 데이터를 제외한 모든 회원 개인정보는 즉각 소멸 처리되며, 어떤 사유로도 복구가 불가능합니다.</p>
            <ul className="list-disc pl-5 space-y-1 font-medium text-foreground/90">
              <li>가입 이메일, 회원 성명, 전문가 프로필 및 설정 데이터 삭제</li>
              <li>원료 위험도 평가, AI 채팅 분석 상담 이력 삭제</li>
              <li>위해제품 식별 및 법률 채팅 질의 응답 로그 즉각 파기</li>
            </ul>
            <p className="text-[11px] font-semibold text-destructive/90 pt-1">
              ※ 탈퇴 완료 후에는 동일한 이메일로 즉시 재가입은 가능하나, 이전의 모든 활동 로그는 복원되지 않습니다.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Form */}
      <Card className="border border-border bg-card shadow-sm">
        <CardContent className="p-6 space-y-5">
          {error && (
            <div className="flex gap-2 p-3.5 bg-destructive/10 text-destructive border border-destructive/20 rounded-lg text-xs font-semibold items-center">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          {/* Consent Checkbox */}
          <div className="flex items-start space-x-2.5 pt-1">
            <Checkbox
              id="withdrawal-agree"
              checked={isChecked}
              onCheckedChange={(checked) => setIsChecked(checked === true)}
              className="mt-0.5 border-border data-[state=checked]:bg-destructive data-[state=checked]:border-destructive"
            />
            <Label
              htmlFor="withdrawal-agree"
              className="text-xs leading-relaxed text-muted-foreground font-semibold cursor-pointer select-none"
            >
              위 안내 사항을 모두 숙지하였으며, 이에 동의하고 탈퇴를 진행합니다.
            </Label>
          </div>

          {/* Dialog Trigger / Submit Button */}
          <div className="pt-2">
            <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
              <DialogTrigger asChild>
                <Button
                  type="button"
                  disabled={!isChecked || isLoading}
                  className="w-full h-11 bg-destructive text-destructive-foreground hover:bg-destructive/90 shadow-sm"
                >
                  {isLoading ? (
                    <>
                      <Spinner className="mr-2 h-4 w-4" />
                      탈퇴 진행 중...
                    </>
                  ) : (
                    <>
                      <Trash2 className="h-4 w-4 mr-2" />
                      회원 탈퇴 신청
                    </>
                  )}
                </Button>
              </DialogTrigger>

              <DialogContent className="max-w-sm rounded-xl border border-border bg-card">
                <DialogHeader className="text-center sm:text-left space-y-1.5">
                  <DialogTitle className="text-base font-bold text-foreground">정말 탈퇴하시겠습니까?</DialogTitle>
                  <DialogDescription className="text-xs text-muted-foreground">
                    탈퇴 시 모든 활동 데이터가 안전하게 삭제되며 복구할 수 없습니다. 탈퇴 후에는 동일한 이메일로 다시 가입하실 수 있습니다.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter className="flex flex-row gap-2 mt-4 sm:justify-end">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setIsDialogOpen(false)}
                    className="flex-1 sm:flex-none border-border h-9 text-xs"
                  >
                    취소
                  </Button>
                  <Button
                    type="button"
                    variant="destructive"
                    onClick={handleWithdrawal}
                    className="flex-1 sm:flex-none bg-destructive hover:bg-destructive/90 h-9 text-xs"
                  >
                    탈퇴하기
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Cryptography notice */}
          <div className="flex items-center gap-1.5 text-[10px] text-muted-foreground justify-center">
            <Lock className="h-3 w-3" />
            <span>회원 탈퇴는 256-bit 보안 프로토콜의 인증 절차를 거쳐 처리됩니다.</span>
          </div>

        </CardContent>
      </Card>
    </div>
  )
}
