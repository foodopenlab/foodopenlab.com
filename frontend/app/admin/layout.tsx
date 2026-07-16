"use client"

import { useEffect, useState } from "react"
import { usePathname, useRouter } from "next/navigation"
import { isAdminLoggedIn, removeAdminSession } from "@/lib/admin/auth"
import { AdminSidebar, AdminMobileNav } from "@/components/admin/admin-sidebar"
import { AdminHeader } from "@/components/admin/admin-header"
import { Drawer, DrawerContent } from "@/components/ui/drawer"
import { Toaster } from "@/components/ui/toaster"

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname()
  const router = useRouter()
  const [gate, setGate] = useState<"login" | "shell" | "wait">("wait")
  const [navOpen, setNavOpen] = useState(false)

  useEffect(() => {
    if (pathname === "/admin/login") {
      setGate("login")
      return
    }
    if (!isAdminLoggedIn()) {
      removeAdminSession()
      router.replace("/admin/login")
      setGate("wait")
      return
    }
    setGate("shell")
  }, [pathname, router])

  useEffect(() => {
    setNavOpen(false)
  }, [pathname])

  if (pathname === "/admin/login") {
    return (
      <>
        {children}
        <Toaster />
      </>
    )
  }

  if (gate !== "shell" || !isAdminLoggedIn()) {
    return (
      <div className="flex min-h-dvh items-center justify-center bg-background px-4 text-sm text-muted-foreground">
        로딩 중…
      </div>
    )
  }

  return (
    <div className="flex min-h-dvh flex-col bg-background lg:h-dvh lg:flex-row">
      <AdminSidebar className="hidden lg:flex" />

      <Drawer open={navOpen} onOpenChange={setNavOpen} direction="left">
        <DrawerContent className="h-full max-h-none w-[min(100%,17.5rem)] rounded-none border-r p-0">
          <AdminMobileNav onNavigate={() => setNavOpen(false)} />
        </DrawerContent>
      </Drawer>

      <div className="flex min-w-0 flex-1 flex-col overflow-hidden lg:rounded-tl-3xl lg:bg-muted/20">
        <AdminHeader onMenuOpen={() => setNavOpen(true)} />
        <main className="flex-1 overflow-x-hidden overflow-y-auto p-4 sm:p-5 lg:p-8">{children}</main>
      </div>
      <Toaster />
    </div>
  )
}
