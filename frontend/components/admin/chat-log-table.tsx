"use client"

import { Button } from "@/components/ui/button"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"

export type ChatSessionRow = {
  session_id: string
  chat_type: string
  company_type: string | null
  message_count: number
  created_at: string
  updated_at: string
}

type Props = {
  rows: ChatSessionRow[]
  onOpenDetail: (sessionId: string, chatType: string) => void
}

function typeBadge(t: string) {
  if (t === "analysis" || t === "ingredient")
    return <Badge className="bg-blue-500/20 text-blue-300">원료 분석</Badge>
  if (t === "regulation") return <Badge className="bg-emerald-500/20 text-emerald-300">법규 채팅</Badge>
  return <Badge variant="secondary">{t}</Badge>
}

export function ChatLogTable({ rows, onOpenDetail }: Props) {
  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>유형</TableHead>
          <TableHead>세션ID</TableHead>
          <TableHead>업종</TableHead>
          <TableHead>메시지 수</TableHead>
          <TableHead>생성일</TableHead>
          <TableHead className="text-right">상세</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {rows.map((r) => (
          <TableRow key={r.session_id}>
            <TableCell>{typeBadge(r.chat_type)}</TableCell>
            <TableCell className="font-mono text-xs text-muted-foreground">
              {r.session_id.slice(0, 8)}…
            </TableCell>
            <TableCell className="text-muted-foreground">
              {r.chat_type === "regulation" ? r.company_type ?? "—" : "—"}
            </TableCell>
            <TableCell>{r.message_count}</TableCell>
            <TableCell className="whitespace-nowrap text-muted-foreground">
              {new Date(r.created_at).toLocaleString("ko-KR")}
            </TableCell>
            <TableCell className="text-right">
              <Button
                type="button"
                size="sm"
                variant="outline"
                onClick={() => onOpenDetail(r.session_id, r.chat_type)}
              >
                상세보기
              </Button>
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
