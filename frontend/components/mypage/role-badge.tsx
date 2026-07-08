import { Badge } from "@/components/ui/badge"

export function RoleBadge({ role }: { role: "user" | "expert" }) {
  if (role === "expert") {
    return (
      <Badge className="bg-blue-500/15 text-blue-500 border border-blue-500/30 hover:bg-blue-500/15 px-2.5 py-0.5 rounded text-[11px] font-semibold tracking-wide">
        전문가회원
      </Badge>
    )
  }
  return (
    <Badge className="bg-zinc-500/15 text-zinc-500 border border-zinc-500/30 hover:bg-zinc-500/15 px-2.5 py-0.5 rounded text-[11px] font-semibold tracking-wide">
      일반회원
    </Badge>
  )
}
