"use client"

import { useEffect, useState } from "react"
import { usePathname } from "next/navigation"
import Link from "next/link"
import { LogOut, ShieldCheck } from "lucide-react"
import { cn } from "@/lib/utils"
import { getAdminDisplayName, removeAdminSession } from "@/lib/admin/auth"
import { ADMIN_NAV_ITEMS, isAdminNavActive } from "@/lib/admin/admin-nav"
import { Button } from "@/components/ui/button"

type AdminNavListProps = {
  variant?: "desktop" | "drawer"
  onNavigate?: () => void
}

export function AdminNavList({ variant = "desktop", onNavigate }: AdminNavListProps) {
  const pathname = usePathname()

  return (
    <nav className={cn("flex flex-col gap-1", variant === "drawer" ? "px-2" : "px-3")}>
      {ADMIN_NAV_ITEMS.map(({ href, label, icon: Icon, section }) => {
        const active = isAdminNavActive(pathname, href)
        return (
          <div key={href}>
            {section && (
              <p className="mt-3 mb-1 px-4 text-[11px] font-semibold uppercase tracking-wider text-muted-foreground/70">
                {section}
              </p>
            )}
            <Link
              href={href}
              onClick={onNavigate}
              className={cn(
                "flex min-h-11 items-center gap-3 px-4 py-3 text-sm font-medium transition-all",
                variant === "desktop" && active
                  ? "rounded-l-2xl rounded-r-none bg-background text-primary shadow-sm"
                  : variant === "desktop"
                    ? "rounded-xl text-muted-foreground hover:bg-background/40 hover:text-foreground"
                    : active
                      ? "rounded-xl bg-primary/10 text-primary"
                      : "rounded-xl text-muted-foreground hover:bg-muted/50 hover:text-foreground",
              )}
            >
              <Icon className="size-4 shrink-0" aria-hidden />
              <span>{label}</span>
            </Link>
          </div>
        )
      })}
    </nav>
  )
}

type AdminSidebarProps = {
  className?: string
}

export function AdminSidebar({ className }: AdminSidebarProps) {
  const pathname = usePathname()
  const [label, setLabel] = useState("관리자")

  useEffect(() => {
    setLabel(getAdminDisplayName())
  }, [pathname])

  const logout = () => {
    removeAdminSession()
    window.location.href = "/admin/login"
  }

  return (
    <aside
      className={cn(
        "relative flex h-full w-full max-w-[17rem] shrink-0 flex-col bg-card/80 lg:h-screen lg:w-[17rem]",
        className,
      )}
    >
      <div className="px-4 pb-4 pt-5 lg:px-5 lg:pb-6 lg:pt-6">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <ShieldCheck className="size-5" aria-hidden />
          </div>
          <div className="min-w-0">
            <div className="truncate text-lg font-bold tracking-tight text-foreground">HACCP</div>
            <div className="truncate text-xs text-muted-foreground" title={label}>
              {label}
            </div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto">
        <AdminNavList variant="desktop" />
      </div>

      <div className="border-t border-border/60 p-3">
        <Button
          type="button"
          variant="ghost"
          className="h-11 w-full justify-start gap-3 rounded-xl text-muted-foreground hover:bg-background/40 hover:text-foreground"
          onClick={logout}
        >
          <LogOut className="size-4" aria-hidden />
          로그아웃
        </Button>
      </div>
    </aside>
  )
}

export function AdminMobileNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname()
  const [label, setLabel] = useState("관리자")

  useEffect(() => {
    setLabel(getAdminDisplayName())
  }, [pathname])

  const logout = () => {
    removeAdminSession()
    window.location.href = "/admin/login"
  }

  return (
    <div className="flex h-full flex-col">
      <div className="border-b border-border/60 px-4 py-4">
        <div className="flex items-center gap-3">
          <div className="flex size-10 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <ShieldCheck className="size-5" aria-hidden />
          </div>
          <div className="min-w-0">
            <div className="truncate text-base font-bold text-foreground">HACCP Admin</div>
            <div className="truncate text-xs text-muted-foreground">{label}</div>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto py-2">
        <AdminNavList variant="drawer" onNavigate={onNavigate} />
      </div>

      <div className="border-t border-border/60 p-3">
        <Button
          type="button"
          variant="ghost"
          className="h-11 w-full justify-start gap-3 rounded-xl"
          onClick={() => {
            onNavigate?.()
            logout()
          }}
        >
          <LogOut className="size-4" aria-hidden />
          로그아웃
        </Button>
      </div>
    </div>
  )
}
