"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { User, Lock, UserMinus, FileText, SlidersHorizontal } from "lucide-react"
import { RoleBadge } from "./role-badge"
import { cn } from "@/lib/utils"

interface SidebarProps {
  userName: string
  role: "user" | "expert"
}

export function Sidebar({ userName, role }: SidebarProps) {
  const pathname = usePathname()

  const menuItems = [
    {
      title: "기본 정보",
      href: "/mypage",
      icon: User,
      show: true,
    },
    {
      title: "일일 리포트",
      href: "/mypage/reports",
      icon: FileText,
      show: role === "expert",
    },
    {
      title: "업종/관심 설정",
      href: "/mypage/industry",
      icon: SlidersHorizontal,
      show: role === "expert",
    },
    {
      title: "비밀번호 변경",
      href: "/mypage/password",
      icon: Lock,
      show: true,
    },
    {
      title: "회원 탈퇴",
      href: "/mypage/withdraw",
      icon: UserMinus,
      show: true,
    },
  ]

  return (
    <aside className="w-full shrink-0 flex-col md:w-56 bg-card border border-border rounded-xl p-5 shadow-sm space-y-6">
      <div className="flex flex-col items-center text-center space-y-2 border-b border-border/60 pb-5">
        <div className="relative flex h-14 w-14 items-center justify-center rounded-full bg-primary/10 text-primary border border-primary/20 shadow-inner">
          <User className="h-7 w-7" />
        </div>
        <div className="space-y-1">
          <h2 className="text-base font-semibold text-foreground truncate max-w-[180px]">{userName}</h2>
          <div className="flex justify-center pt-0.5">
            <RoleBadge role={role} />
          </div>
        </div>
      </div>

      <nav className="flex flex-row md:flex-col overflow-x-auto md:overflow-x-visible gap-1 pb-2 md:pb-0">
        {menuItems
          .filter((item) => item.show)
          .map((item) => {
            const Icon = item.icon
            const active = pathname === item.href

            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-lg transition-all duration-200 shrink-0",
                  active
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:bg-muted/40 hover:text-foreground"
                )}
              >
                <Icon className={cn("h-4 w-4 shrink-0", active ? "text-primary" : "text-muted-foreground/80")} />
                <span>{item.title}</span>
              </Link>
            )
          })}
      </nav>
    </aside>
  )
}
