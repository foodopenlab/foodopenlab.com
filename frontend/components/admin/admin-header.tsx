"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"
import { Bell, Menu, Search } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme/theme-toggle"

const titles: { prefix: string; title: string }[] = [
  { prefix: "/admin/siliconvalley", title: "실리콘밸리" },
  { prefix: "/admin/logs", title: "통합 로그" },
  { prefix: "/admin/whitelist", title: "화이트리스트" },
  { prefix: "/admin/api-stats", title: "API 통계" },
  { prefix: "/admin/ai-settings", title: "AI 설정" },
  { prefix: "/admin/chat-logs", title: "채팅 로그" },
  { prefix: "/admin/data-sync", title: "데이터 동기화" },
  { prefix: "/admin/hazard-alerts", title: "위해 알림" },
  { prefix: "/admin/login", title: "관리자 로그인" },
  { prefix: "/admin", title: "대시보드" },
]

function titleForPath(pathname: string | null): string {
  if (!pathname) return "관리자"
  const sorted = [...titles].sort((a, b) => b.prefix.length - a.prefix.length)
  for (const { prefix, title } of sorted) {
    if (pathname === prefix || pathname.startsWith(prefix + "/")) return title
  }
  return "관리자"
}

function formatNow(d: Date) {
  return d.toLocaleString("ko-KR", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    weekday: "short",
  })
}

type AdminHeaderProps = {
  onMenuOpen?: () => void
}

export function AdminHeader({ onMenuOpen }: AdminHeaderProps) {
  const pathname = usePathname()
  const [now, setNow] = useState(() => new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  return (
    <header className="sticky top-0 z-30 flex min-h-14 shrink-0 items-center gap-3 border-b border-border/60 bg-background/95 px-4 py-2 backdrop-blur-sm sm:gap-4 sm:px-6 lg:h-16">
      <Button
        type="button"
        variant="ghost"
        size="icon"
        className="size-10 shrink-0 rounded-xl lg:hidden"
        onClick={onMenuOpen}
        aria-label="메뉴 열기"
      >
        <Menu className="size-5" />
      </Button>

      <div className="min-w-0 flex-1">
        <h1 className="truncate text-base font-semibold text-foreground sm:text-lg lg:text-xl">
          {titleForPath(pathname)}
        </h1>
        <time className="hidden text-xs text-muted-foreground sm:block" dateTime={now.toISOString()}>
          {formatNow(now)}
        </time>
      </div>

      <div className="hidden max-w-xs flex-1 lg:block xl:max-w-md">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="대시보드 검색..."
            className="h-10 rounded-full border-border/60 bg-card pl-10"
            aria-label="대시보드 검색"
          />
        </div>
      </div>

      <div className="flex shrink-0 items-center gap-1 sm:gap-2">
        <ThemeToggle />
        <Button type="button" variant="ghost" size="icon" className="size-10 rounded-full" aria-label="알림">
          <Bell className="size-4" />
        </Button>
        <div className="flex size-9 items-center justify-center rounded-full bg-primary/15 text-sm font-semibold text-primary">
          A
        </div>
      </div>
    </header>
  )
}
