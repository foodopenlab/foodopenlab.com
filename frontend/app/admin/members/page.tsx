"use client"

import { useCallback, useEffect, useState } from "react"
import { adminFetch } from "@/lib/admin/auth"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Users, RefreshCw, ArrowUpCircle, ArrowDownCircle } from "lucide-react"
import { cn } from "@/lib/utils"

type Member = {
  id: string
  email: string
  name: string | null
  auth_provider: string
  is_expert: boolean
  last_login: string | null
  created_at: string
}

const PROVIDER_LABEL: Record<string, string> = {
  email: "이메일",
  google: "구글",
  kakao: "카카오",
  naver: "네이버",
}

export default function AdminMembersPage() {
  const [list, setList] = useState<Member[]>([])
  const [loading, setLoading] = useState(false)
  const [busyEmail, setBusyEmail] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  const fetchList = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const res = await adminFetch("/admin/members")
      if (!res.ok) throw new Error("회원 목록을 불러오지 못했습니다.")
      setList((await res.json()) || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : "목록 조회 중 오류가 발생했습니다.")
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void fetchList()
  }, [fetchList])

  const toggleExpert = async (member: Member) => {
    const action = member.is_expert ? "demote" : "promote"
    setBusyEmail(member.email)
    setError(null)
    setSuccess(null)
    try {
      const res = await adminFetch(`/admin/members/${encodeURIComponent(member.email)}/${action}`, {
        method: "POST",
      })
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}))
        throw new Error(typeof errData.detail === "string" ? errData.detail : "처리 중 오류가 발생했습니다.")
      }
      setSuccess(
        member.is_expert
          ? `${member.email} 님의 전문가 승격을 해제했습니다.`
          : `${member.email} 님을 전문가로 승격했습니다.`,
      )
      await fetchList()
    } catch (err) {
      setError(err instanceof Error ? err.message : "처리에 실패했습니다.")
    } finally {
      setBusyEmail(null)
    }
  }

  return (
    <div className="space-y-6 text-foreground">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-xl font-bold text-foreground flex items-center gap-2">
            <Users className="h-5 w-5 text-primary" />
            회원 관리 · 전문가 승격
          </h1>
          <p className="text-xs text-muted-foreground mt-0.5">
            가입한 회원을 확인하고, 전문가로 승격하거나 승격을 해제합니다. 승격은 다음 로그인부터 전문가 권한으로 반영됩니다.
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

      {error && <div className="text-xs text-red-500 bg-red-500/10 p-3 rounded-lg border border-red-500/20">{error}</div>}
      {success && <div className="text-xs text-emerald-500 bg-emerald-500/10 p-3 rounded-lg border border-emerald-500/20">{success}</div>}

      <div className="rounded-xl border border-border bg-card overflow-x-auto">
        <Table className="text-xs min-w-[820px]">
          <TableHeader className="bg-muted/30">
            <TableRow>
              <TableHead className="w-[220px]">이메일</TableHead>
              <TableHead className="w-[120px]">이름</TableHead>
              <TableHead className="w-[80px]">가입 경로</TableHead>
              <TableHead className="w-[90px]">상태</TableHead>
              <TableHead className="w-[148px]">가입일</TableHead>
              <TableHead className="w-[148px]">마지막 로그인</TableHead>
              <TableHead className="w-[132px] text-center sticky right-0 bg-muted/30">전문가 권한</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {loading && list.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">로딩 중...</TableCell>
              </TableRow>
            ) : list.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-32 text-center text-muted-foreground">가입한 회원이 없습니다.</TableCell>
              </TableRow>
            ) : (
              list.map((m) => (
                <TableRow key={m.id} className="hover:bg-muted/10">
                  <TableCell className="font-semibold text-foreground">{m.email}</TableCell>
                  <TableCell className="text-muted-foreground">{m.name || "—"}</TableCell>
                  <TableCell className="text-muted-foreground">{PROVIDER_LABEL[m.auth_provider] || m.auth_provider}</TableCell>
                  <TableCell>
                    <span
                      className={cn(
                        "inline-flex items-center rounded-full px-2 py-0.5 text-[11px] font-semibold",
                        m.is_expert
                          ? "bg-primary/15 text-primary"
                          : "bg-muted text-muted-foreground",
                      )}
                    >
                      {m.is_expert ? "전문가" : "일반"}
                    </span>
                  </TableCell>
                  <TableCell className="font-mono text-muted-foreground whitespace-nowrap">
                    {new Date(m.created_at).toLocaleString("ko-KR")}
                  </TableCell>
                  <TableCell className="font-mono text-muted-foreground whitespace-nowrap">
                    {m.last_login ? new Date(m.last_login).toLocaleString("ko-KR") : "—"}
                  </TableCell>
                  <TableCell className="text-center sticky right-0 bg-card">
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      className={cn(
                        "h-7 gap-1 px-2 text-[11px]",
                        m.is_expert
                          ? "text-destructive border-destructive/40 hover:bg-destructive/10 hover:text-destructive"
                          : "text-primary border-primary/40 hover:bg-primary/10 hover:text-primary",
                      )}
                      disabled={busyEmail === m.email}
                      onClick={() => void toggleExpert(m)}
                    >
                      {m.is_expert ? (
                        <>
                          <ArrowDownCircle className="h-3 w-3" />
                          {busyEmail === m.email ? "처리 중..." : "승격 해제"}
                        </>
                      ) : (
                        <>
                          <ArrowUpCircle className="h-3 w-3" />
                          {busyEmail === m.email ? "처리 중..." : "전문가 승격"}
                        </>
                      )}
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  )
}
