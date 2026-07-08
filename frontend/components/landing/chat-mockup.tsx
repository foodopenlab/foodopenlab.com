import { Badge } from "@/components/ui/badge"
import { Bot, User } from "lucide-react"

export function ChatMockup() {
  return (
    <div className="w-full max-w-md rounded-xl border border-border bg-card p-4 shadow-2xl shadow-primary/5">
      {/* Window Header */}
      <div className="mb-4 flex items-center gap-2">
        <div className="h-3 w-3 rounded-full bg-red-500/60" />
        <div className="h-3 w-3 rounded-full bg-yellow-500/60" />
        <div className="h-3 w-3 rounded-full bg-green-500/60" />
        <span className="ml-2 text-xs text-muted-foreground">HACCP Monitor AI</span>
      </div>

      {/* Chat Messages */}
      <div className="space-y-4">
        {/* User Message */}
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-secondary">
            <User className="h-4 w-4 text-muted-foreground" />
          </div>
          <div className="rounded-lg bg-secondary px-4 py-2">
            <p className="text-sm text-foreground">이번 달 대두 관련 회수 있어?</p>
          </div>
        </div>

        {/* AI Response */}
        <div className="flex items-start gap-3">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary">
            <Bot className="h-4 w-4 text-primary-foreground" />
          </div>
          <div className="flex-1 space-y-3 rounded-lg bg-secondary/50 px-4 py-3">
            <p className="text-sm text-foreground">
              네, 이번 달 대두 관련 회수 건이 <span className="font-semibold text-primary">3건</span> 확인되었습니다.
            </p>

            {/* Risk Badges */}
            <div className="flex flex-wrap gap-2">
              <Badge className="bg-red-500/20 text-red-400 hover:bg-red-500/30">HIGH 1건</Badge>
              <Badge className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30">MEDIUM 1건</Badge>
              <Badge className="bg-green-500/20 text-green-400 hover:bg-green-500/30">LOW 1건</Badge>
            </div>

            {/* Mini Table */}
            <div className="overflow-hidden rounded-md border border-border">
              <table className="w-full text-xs">
                <thead className="bg-secondary">
                  <tr>
                    <th className="px-2 py-1.5 text-left font-medium text-muted-foreground">원료명</th>
                    <th className="px-2 py-1.5 text-left font-medium text-muted-foreground">위험도</th>
                    <th className="px-2 py-1.5 text-left font-medium text-muted-foreground">회수일</th>
                  </tr>
                </thead>
                <tbody className="text-foreground">
                  <tr className="border-t border-border">
                    <td className="px-2 py-1.5">대두단백</td>
                    <td className="px-2 py-1.5">
                      <span className="text-red-400">HIGH</span>
                    </td>
                    <td className="px-2 py-1.5">2025-05-10</td>
                  </tr>
                  <tr className="border-t border-border">
                    <td className="px-2 py-1.5">대두유</td>
                    <td className="px-2 py-1.5">
                      <span className="text-yellow-400">MEDIUM</span>
                    </td>
                    <td className="px-2 py-1.5">2025-05-08</td>
                  </tr>
                  <tr className="border-t border-border">
                    <td className="px-2 py-1.5">대두레시틴</td>
                    <td className="px-2 py-1.5">
                      <span className="text-green-400">LOW</span>
                    </td>
                    <td className="px-2 py-1.5">2025-05-05</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      {/* Input Field */}
      <div className="mt-4 flex items-center gap-2 rounded-lg border border-border bg-secondary/50 px-3 py-2">
        <input
          type="text"
          placeholder="무엇이든 질문하세요."
          className="flex-1 bg-transparent text-sm text-foreground placeholder:text-muted-foreground focus:outline-none"
          readOnly
        />
        <div className="flex h-6 w-6 items-center justify-center rounded-md bg-primary">
          <svg className="h-3 w-3 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        </div>
      </div>
    </div>
  )
}
