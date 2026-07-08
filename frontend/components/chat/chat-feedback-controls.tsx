"use client"

import { useEffect, useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"
import { ThumbsUp, ThumbsDown, Check, AlertCircle } from "lucide-react"

type SaveState = "idle" | "saving" | "saved" | "error"

function getRoleFromToken(token: string | null): string | null {
  if (!token) return null
  try {
    const parts = token.split(".")
    if (parts.length < 2) return null
    const payload = JSON.parse(atob(parts[1]))
    return payload.role || null
  } catch {
    return null
  }
}

export function ChatFeedbackControls({
  messageId,
  sessionKey,
}: {
  messageId?: string | null
  sessionKey: string
}) {
  const [role, setRole] = useState<string | null>(null)
  const [token, setToken] = useState<string | null>(null)
  
  const [satisfaction, setSatisfaction] = useState<boolean | null>(null)
  const [label, setLabel] = useState<"correct" | "partial" | "incorrect" | null>(null)
  const [memo, setMemo] = useState("")
  
  const [satState, setSatState] = useState<SaveState>("idle")
  const [expState, setExpState] = useState<SaveState>("idle")

  useEffect(() => {
    const t = localStorage.getItem("access_token")
    setToken(t)
    setRole(getRoleFromToken(t))
  }, [])

  if (!messageId) return null

  const handleSatisfaction = async (isPositive: boolean) => {
    setSatisfaction(isPositive)
    setSatState("saving")
    try {
      const res = await fetch(`/api/chat/messages/${messageId}/feedback/satisfaction`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ is_positive: isPositive }),
      })
      if (!res.ok) throw new Error("failed")
      setSatState("saved")
    } catch {
      setSatState("error")
    }
  }

  const handleExpertFeedback = async (nextLabel: "correct" | "partial" | "incorrect") => {
    setLabel(nextLabel)
    setExpState("saving")
    try {
      const res = await fetch(`/api/chat/messages/${messageId}/feedback/expert`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ label: nextLabel, memo: memo.trim() || undefined }),
      })
      if (!res.ok) throw new Error("failed")
      setExpState("saved")
    } catch {
      setExpState("error")
    }
  }

  const isExpertOrAdmin = role === "expert" || role === "admin"

  return (
    <div className="mt-4 space-y-3 rounded-xl border border-border/60 bg-muted/30 p-3 text-xs text-foreground">
      {/* Satisfaction Feedback (Thumbs Up/Down) */}
      <div className={cn("flex items-center justify-between", isExpertOrAdmin && "border-b border-border/40 pb-2")}>
        <span className="font-semibold text-foreground">답변 만족도 평가</span>
        <div className="flex gap-2">
          <Button
            type="button"
            variant={satisfaction === true ? "default" : "outline"}
            className={cn("h-7 px-2.5 text-xs gap-1", satisfaction === true && "bg-emerald-600 hover:bg-emerald-700 text-white")}
            onClick={() => void handleSatisfaction(true)}
            disabled={satState === "saving"}
          >
            <ThumbsUp className="h-3 w-3" />
            유용함
          </Button>
          <Button
            type="button"
            variant={satisfaction === false ? "default" : "outline"}
            className={cn("h-7 px-2.5 text-xs gap-1", satisfaction === false && "bg-rose-600 hover:bg-rose-700 text-white")}
            onClick={() => void handleSatisfaction(false)}
            disabled={satState === "saving"}
          >
            <ThumbsDown className="h-3 w-3" />
            미흡함
          </Button>
        </div>
      </div>

      {/* Expert Verification Labeling */}
      {isExpertOrAdmin && (
        <div className="space-y-2">
          <span className="font-semibold text-foreground block">전문가 정합성 라벨링</span>
          <div className="grid grid-cols-3 gap-2">
            <Button
              type="button"
              variant={label === "correct" ? "default" : "outline"}
              className={cn(
                "h-7 text-xs",
                label === "correct" && "bg-primary text-primary-foreground font-semibold"
              )}
              onClick={() => void handleExpertFeedback("correct")}
              disabled={expState === "saving"}
            >
              {label === "correct" && expState === "saved" && <Check className="mr-1 h-3 w-3" />}
              정답 (Correct)
            </Button>
            <Button
              type="button"
              variant={label === "partial" ? "default" : "outline"}
              className={cn(
                "h-7 text-xs",
                label === "partial" && "bg-amber-600 hover:bg-amber-700 text-white font-semibold"
              )}
              onClick={() => void handleExpertFeedback("partial")}
              disabled={expState === "saving"}
            >
              {label === "partial" && expState === "saved" && <Check className="mr-1 h-3 w-3" />}
              부분정답
            </Button>
            <Button
              type="button"
              variant={label === "incorrect" ? "default" : "outline"}
              className={cn(
                "h-7 text-xs",
                label === "incorrect" && "bg-red-600 hover:bg-red-700 text-white font-semibold"
              )}
              onClick={() => void handleExpertFeedback("incorrect")}
              disabled={expState === "saving"}
            >
              {label === "incorrect" && expState === "saved" && <Check className="mr-1 h-3 w-3" />}
              오답 (Incorrect)
            </Button>
          </div>

          {/* Optional Memo Input */}
          <div className="flex gap-1.5 mt-2">
            <Input
              value={memo}
              onChange={(e) => setMemo(e.target.value)}
              placeholder="평가 메모를 입력하세요 (선택)"
              className="h-7 text-xs flex-1 bg-background"
              disabled={expState === "saving"}
            />
            {label && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="h-7 text-xs"
                onClick={() => void handleExpertFeedback(label)}
                disabled={expState === "saving"}
              >
                메모반영
              </Button>
            )}
          </div>
        </div>
      )}

      {/* Save status message */}
      <div className="flex items-center gap-1 text-[11px] text-muted-foreground">
        {satState === "saving" && (
          <span className="animate-pulse">평가를 저장하는 중입니다...</span>
        )}
        {isExpertOrAdmin && expState === "saving" && (
          <span className="animate-pulse">정합성 평가를 저장하는 중입니다...</span>
        )}
        {satState === "saved" && !isExpertOrAdmin && (
          <span className="text-emerald-500 flex items-center gap-0.5">
            <Check className="h-3 w-3" /> 만족도 저장됨
          </span>
        )}
        {isExpertOrAdmin && satState === "saved" && expState === "saved" && (
          <span className="text-emerald-500 font-medium flex items-center gap-0.5">
            <Check className="h-3 w-3" /> 모든 피드백 저장 완료
          </span>
        )}
        {isExpertOrAdmin && satState === "saved" && expState !== "saved" && (
          <span className="text-emerald-500 flex items-center gap-0.5">
            <Check className="h-3 w-3" /> 만족도 저장됨
          </span>
        )}
        {isExpertOrAdmin && expState === "saved" && satState !== "saved" && (
          <span className="text-emerald-500 flex items-center gap-0.5">
            <Check className="h-3 w-3" /> 정합성 평가 저장됨
          </span>
        )}
        {(satState === "error" || (isExpertOrAdmin && expState === "error")) && (
          <span className="text-destructive flex items-center gap-0.5">
            <AlertCircle className="h-3 w-3" /> 저장 중 오류가 발생했습니다.
          </span>
        )}
      </div>
    </div>
  )
}
