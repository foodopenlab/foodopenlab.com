"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Edit2, Check, X } from "lucide-react"
import { useToast } from "@/hooks/use-toast"
import { Spinner } from "@/components/ui/spinner"

interface InlineNameEditorProps {
  initialName: string
  token: string
  onNameUpdated: (newName: string) => void
}

export function InlineNameEditor({ initialName, token, onNameUpdated }: InlineNameEditorProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [name, setName] = useState(initialName)
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleStartEditing = () => {
    setName(initialName)
    setError(null)
    setIsEditing(true)
  }

  const handleCancel = () => {
    setName(initialName)
    setError(null)
    setIsEditing(false)
  }

  const handleSave = async () => {
    const trimmedName = name.trim()
    
    if (trimmedName.length < 2 || trimmedName.length > 30) {
      setError("이름은 2자 이상, 30자 이하로 입력해 주세요.")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const res = await fetch("/api/mypage/profile", {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
          Accept: "application/json",
        },
        body: JSON.stringify({ name: trimmedName }),
      })

      const data = await res.json().catch(() => null)

      if (!res.ok) {
        // Validation or other backend error
        const errMsg = data?.detail?.[0]?.msg || data?.detail || "이름 변경에 실패했습니다."
        setError(errMsg)
        return
      }

      const updatedName = data.name || trimmedName
      onNameUpdated(updatedName)
      setIsEditing(false)
      
      toast({
        title: "이름 변경 완료",
        description: "회원님의 이름이 성공적으로 변경되었습니다.",
      })
    } catch {
      setError("네트워크 오류로 이름을 변경할 수 없습니다.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col gap-2 p-5 bg-card border border-border rounded-xl shadow-sm">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="space-y-1">
          <label htmlFor="name-editor-input" className="text-xs text-muted-foreground font-semibold uppercase tracking-wider">이름 / 상호명</label>
          {isEditing ? (
            <div className="relative max-w-sm">
              <Input
                id="name-editor-input"
                value={name}
                onChange={(e) => {
                  setName(e.target.value)
                  setError(null)
                }}
                disabled={isLoading}
                placeholder="이름 또는 표시명을 입력해 주세요"
                className="h-10 pr-10 border-border bg-input text-foreground text-sm"
                autoFocus
              />
              {error && <p className="text-xs text-destructive mt-1 font-medium">{error}</p>}
            </div>
          ) : (
            <p className="text-lg font-bold text-foreground">{initialName}</p>
          )}
        </div>

        <div className="flex gap-2 shrink-0 self-end sm:self-auto">
          {isEditing ? (
            <>
              <Button
                variant="outline"
                size="sm"
                onClick={handleCancel}
                disabled={isLoading}
                className="h-9 px-3 border-border hover:bg-muted"
              >
                <X className="h-4 w-4 mr-1.5" />
                취소
              </Button>
              <Button
                variant="default"
                size="sm"
                onClick={handleSave}
                disabled={isLoading}
                className="h-9 px-3 bg-primary text-primary-foreground hover:bg-primary/90"
              >
                {isLoading ? (
                  <Spinner className="h-4 w-4 mr-1.5" />
                ) : (
                  <Check className="h-4 w-4 mr-1.5" />
                )}
                저장
              </Button>
            </>
          ) : (
            <Button
              variant="outline"
              size="sm"
              onClick={handleStartEditing}
              className="h-9 px-3 border-border hover:bg-muted text-muted-foreground hover:text-foreground"
            >
              <Edit2 className="h-3.5 w-3.5 mr-1.5" />
              이름 수정
            </Button>
          )}
        </div>
      </div>
    </div>
  )
}
