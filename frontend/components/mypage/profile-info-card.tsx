import { Card, CardContent } from "@/components/ui/card"
import { Lock, Mail, Calendar, Clock, UserCheck } from "lucide-react"
import { RoleBadge } from "./role-badge"

interface ProfileInfoCardProps {
  email: string
  role: "user" | "expert"
  createdAt: string
  lastLoginAt: string | null
}

function formatDate(dateStr: string | null | undefined): string {
  if (!dateStr) return "정보 없음"
  try {
    const date = new Date(dateStr)
    const yyyy = date.getFullYear()
    const mm = String(date.getMonth() + 1).padStart(2, "0")
    const dd = String(date.getDate()).padStart(2, "0")
    return `${yyyy}.${mm}.${dd}`
  } catch (err) {
    return dateStr
  }
}

function formatDateTime(dateStr: string | null | undefined): string {
  if (!dateStr) return "정보 없음"
  try {
    const date = new Date(dateStr)
    const yyyy = date.getFullYear()
    const mm = String(date.getMonth() + 1).padStart(2, "0")
    const dd = String(date.getDate()).padStart(2, "0")
    const hh = String(date.getHours()).padStart(2, "0")
    const min = String(date.getMinutes()).padStart(2, "0")
    return `${yyyy}.${mm}.${dd} ${hh}:${min}`
  } catch (err) {
    return dateStr
  }
}

export function ProfileInfoCard({ email, role, createdAt, lastLoginAt }: ProfileInfoCardProps) {
  return (
    <Card className="border border-border bg-card shadow-sm overflow-hidden">
      <CardContent className="p-6 space-y-4">
        {/* Info Rows */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          
          {/* Email (Locked, read-only) */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border/40">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <Mail className="h-4.5 w-4.5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground font-medium">로그인 이메일</p>
                <p className="text-sm font-semibold text-foreground truncate max-w-[200px]">{email}</p>
              </div>
            </div>
            <div className="flex items-center gap-1.5 text-muted-foreground/80 bg-muted px-2 py-1 rounded border border-border/30 text-[11px] font-medium select-none">
              <Lock className="h-3 w-3" />
              <span>변경 불가</span>
            </div>
          </div>

          {/* User Role */}
          <div className="flex items-center justify-between p-3 rounded-lg bg-muted/40 border border-border/40">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
                <UserCheck className="h-4.5 w-4.5" />
              </div>
              <div className="space-y-0.5">
                <p className="text-xs text-muted-foreground font-medium">회원 유형</p>
                <p className="text-sm font-semibold text-foreground">
                  {role === "expert" ? "전문가회원" : "일반회원"}
                </p>
              </div>
            </div>
            <RoleBadge role={role} />
          </div>

          {/* Date Joined */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40 border border-border/40">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
              <Calendar className="h-4.5 w-4.5" />
            </div>
            <div className="space-y-0.5">
              <p className="text-xs text-muted-foreground font-medium">가입일</p>
              <p className="text-sm font-semibold text-foreground">{formatDate(createdAt)}</p>
            </div>
          </div>

          {/* Last Login */}
          <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/40 border border-border/40">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-muted text-muted-foreground">
              <Clock className="h-4.5 w-4.5" />
            </div>
            <div className="space-y-0.5">
              <p className="text-xs text-muted-foreground font-medium">최근 로그인</p>
              <p className="text-sm font-semibold text-foreground">{formatDateTime(lastLoginAt)}</p>
            </div>
          </div>

        </div>
      </CardContent>
    </Card>
  )
}
