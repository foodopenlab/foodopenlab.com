"use client"

import { useEffect, useState, useCallback } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog"
import { ShieldCheck, UserPlus, RefreshCw, User, Trash2 } from "lucide-react"
import { cn } from "@/lib/utils"

type WhitelistItem = {
  email: string
  invited_name?: string | null
  role_desc?: string | null
  added_by: string
  added_at: string
}

export default function AdminWhitelistPage() {
  const [list, setList] = useState<WhitelistItem[]>([])
  const [loading, setLoading] = useState(false)
  const [submitLoading, setSubmitLoading] = useState(false)
  const [deleteLoading, setDeleteLoading] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<WhitelistItem | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Form states
  const [email, setEmail] = useState("")
  const [invitedName, setInvitedName] = useState("")
  const [roleDesc, setRoleDesc] = useState("")

  const fetchList = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminFetch("/admin/whitelist")
      if (!res.ok) throw new Error("화이트리스트 목록을 불러오지 못했습니다.")
      const data = await res.json()
      setList(data || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "목록 조회 중 오류가 발생했습니다.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchList()
  }, [fetchList])

  const handleDelete = async () => {
    if (!deleteTarget) return
    setDeleteLoading(true)
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch(`/admin/whitelist/${encodeURIComponent(deleteTarget.email)}`, {
        method: "DELETE",
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(
          typeof errData.detail === "string" ? errData.detail : "삭제 중 오류가 발생했습니다.",
        )
      }
      setSuccess(`${deleteTarget.email} 항목을 화이트리스트에서 삭제했습니다.`)
      setDeleteTarget(null)
      void fetchList()
    } catch (err) {
      setError(err instanceof Error ? err.message : "삭제에 실패했습니다.")
    } finally {
      setDeleteLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!email.trim()) return

    setSubmitLoading(true)
    setError(null)
    setSuccess(null)

    try {
      const res = await adminFetch("/admin/whitelist", {
        method: "POST",
        body: JSON.stringify({
          email: email.trim(),
          invited_name: invitedName.trim() || undefined,
          role_desc: roleDesc.trim() || undefined,
        }),
      })

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(errData.detail || "등록 중 오류가 발생했습니다.")
      }

      setSuccess("전문가 이메일이 화이트리스트에 성공적으로 추가되었습니다.")
      setEmail("")
      setInvitedName("")
      setRoleDesc("")
      void fetchList()
    } catch (err) {
      setError(err instanceof Error ? err.message : "등록에 실패했습니다.")
    } finally {
      setSubmitLoading(false)
    }
  }

  return (
    <>
      <AlertDialog open={deleteTarget !== null} onOpenChange={(open) => !open && !deleteLoading && setDeleteTarget(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>화이트리스트 삭제</AlertDialogTitle>
            <AlertDialogDescription>
              {deleteTarget ? (
                <>
                  <span className="font-medium text-foreground">{deleteTarget.email}</span> 항목을 삭제합니다.
                  삭제 후 해당 이메일로는 전문가 가입이 불가합니다.
                </>
              ) : null}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel type="button" disabled={deleteLoading}>
              취소
            </AlertDialogCancel>
            <AlertDialogAction
              type="button"
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={deleteLoading}
              onClick={() => void handleDelete()}
            >
              {deleteLoading ? "삭제 중..." : "삭제"}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

    <div className="space-y-6 text-foreground">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
            <ShieldCheck className="h-5 w-5 text-primary" />
            전문가 화이트리스트 관리
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            전문가 회원가입이 가능한 이메일 주소를 관리합니다. 등록된 사용자만 가입 승인 단계로 넘어갈 수 있습니다.
          </p>
        </div>
        <Button
          onClick={() => void fetchList()}
          disabled={loading}
          variant="outline"
          size="sm"
          className="h-8 gap-1.5 self-start sm:self-auto"
        >
          <RefreshCw className={cn("h-3.5 w-3.5", loading && "animate-spin")} />
          새로고침
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-[20rem_1fr]">
        {/* Registration Card (Left) */}
        <Card className="h-fit">
          <CardHeader>
            <CardTitle className="text-sm font-semibold flex items-center gap-1.5">
              <UserPlus className="h-4 w-4 text-primary" />
              전문가 추가 등록
            </CardTitle>
            <CardDescription className="text-xs">
              가입을 허용할 전문가의 정보를 입력하세요.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-muted-foreground">이메일 주소 (필수)</label>
                <Input
                  type="email"
                  required
                  placeholder="expert@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-9 text-xs bg-background"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-muted-foreground">초대 대상 성명</label>
                <Input
                  type="text"
                  placeholder="홍길동"
                  value={invitedName}
                  onChange={(e) => setInvitedName(e.target.value)}
                  className="h-9 text-xs bg-background"
                />
              </div>

              <div className="space-y-1.5">
                <label className="text-[11px] font-semibold text-muted-foreground">역할/소속 설명</label>
                <Input
                  type="text"
                  placeholder="식품안전연구소 책임연구원"
                  value={roleDesc}
                  onChange={(e) => setRoleDesc(e.target.value)}
                  className="h-9 text-xs bg-background"
                />
              </div>

              {error && <div className="text-xs text-red-500 bg-red-500/10 p-3 rounded-lg border border-red-500/20">{error}</div>}
              {success && <div className="text-xs text-emerald-500 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">{success}</div>}

              <Button type="submit" disabled={submitLoading} className="w-full h-9 text-xs mt-2">
                {submitLoading ? "등록 중..." : "화이트리스트 등록"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Whitelist Grid (Right) */}
        <div className="space-y-4 min-w-0">
          <div className="rounded-xl border border-border bg-card overflow-x-auto">
            <Table className="text-xs min-w-[720px]">
              <TableHeader className="bg-muted/30">
                <TableRow>
                  <TableHead className="w-[180px]">이메일 주소</TableHead>
                  <TableHead className="w-[100px]">성명</TableHead>
                  <TableHead>역할/소속 설명</TableHead>
                  <TableHead className="w-[88px]">등록자</TableHead>
                  <TableHead className="w-[148px]">등록 일시</TableHead>
                  <TableHead className="w-[88px] text-center sticky right-0 bg-muted/30">삭제</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {loading && list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="h-32 text-center text-muted-foreground">로딩 중...</TableCell>
                  </TableRow>
                ) : list.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="h-32 text-center text-muted-foreground">등록된 전문가가 없습니다.</TableCell>
                  </TableRow>
                ) : (
                  list.map((item) => (
                    <TableRow key={item.email} className="hover:bg-muted/10">
                      <TableCell className="font-semibold text-foreground">{item.email}</TableCell>
                      <TableCell className="text-muted-foreground">
                        <span className="flex items-center gap-1">
                          <User className="h-3 w-3 text-muted-foreground/60" />
                          {item.invited_name || "—"}
                        </span>
                      </TableCell>
                      <TableCell className="text-muted-foreground">{item.role_desc || "—"}</TableCell>
                      <TableCell className="font-mono text-muted-foreground text-[10px] truncate max-w-[80px]">
                        {item.added_by}
                      </TableCell>
                      <TableCell className="font-mono text-muted-foreground whitespace-nowrap">
                        {new Date(item.added_at).toLocaleString("ko-KR")}
                      </TableCell>
                      <TableCell className="text-center sticky right-0 bg-card">
                        <Button
                          type="button"
                          variant="outline"
                          size="sm"
                          className="h-7 gap-1 px-2 text-[11px] text-destructive border-destructive/40 hover:bg-destructive/10 hover:text-destructive"
                          aria-label={`${item.email} 삭제`}
                          onClick={() => setDeleteTarget(item)}
                          disabled={deleteLoading}
                        >
                          <Trash2 className="h-3 w-3" />
                          삭제
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </div>
      </div>
    </div>
    </>
  )
}
