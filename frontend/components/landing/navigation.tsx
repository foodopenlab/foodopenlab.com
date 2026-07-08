"use client"

import Link from "next/link"
import { usePathname, useRouter } from "next/navigation"
import { Button, buttonVariants } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { Menu, Shield } from "lucide-react"
import { useState, useEffect } from "react"

import { cn } from "@/lib/utils"
import { SeoulWeatherNav } from "@/components/landing/seoul-weather-nav"
import { ThemeToggle } from "@/components/theme/theme-toggle"

const navLinkClass = (active: boolean) =>
  cn(
    buttonVariants({ variant: "ghost", size: "sm" }),
    active && "bg-primary/10 text-primary hover:text-primary",
  )

function getRoleFromToken(token: string | null): string | null {
  if (!token) return null
  try {
    const parts = token.split(".")
    if (parts.length < 2) return null
    const payload = JSON.parse(atob(parts[1]))
    return payload.role || null
  } catch {
    return null
  }
}

export function Navigation() {
  const [isOpen, setIsOpen] = useState(false)
  const pathname = usePathname()
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)
  const [isAdmin, setIsAdmin] = useState(false)

  useEffect(() => {
    const t = localStorage.getItem("access_token")
    setToken(t)
    setIsAdmin(getRoleFromToken(t) === "admin")

    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "access_token") {
        setToken(e.newValue)
        setIsAdmin(getRoleFromToken(e.newValue) === "admin")
      }
    }

    const handleAuthChange = () => {
      const stored = localStorage.getItem("access_token")
      setToken(stored)
      setIsAdmin(getRoleFromToken(stored) === "admin")
    }

    window.addEventListener("storage", handleStorageChange)
    window.addEventListener("auth-state-change", handleAuthChange)

    return () => {
      window.removeEventListener("storage", handleStorageChange)
      window.removeEventListener("auth-state-change", handleAuthChange)
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem("access_token")
    setToken(null)
    setIsAdmin(false)
    window.dispatchEvent(new Event("auth-state-change"))
    router.push("/")
    router.refresh()
  }

  const isActive = (href: string) => pathname === href || pathname.startsWith(`${href}/`)

  const isRecallsActive =
    pathname === "/recalls" ||
    (pathname.startsWith("/recalls/") && !pathname.startsWith("/recalls/stats"))

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="container mx-auto flex h-14 min-w-0 items-center justify-between gap-2 px-3 sm:h-16 sm:gap-3 sm:px-4">
        <Link href="/" className="flex min-w-0 items-center gap-2">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-primary">
            <Shield className="h-5 w-5 text-primary-foreground" />
          </div>
          <span className="truncate text-base font-semibold text-foreground sm:text-lg">
            <span className="sm:hidden">HACCP AI</span>
            <span className="hidden sm:inline">HACCP Monitor AI</span>
          </span>
        </Link>

        <div className="hidden items-center gap-3 md:flex">
          <Link href="/recalls" className={navLinkClass(isRecallsActive)}>
            위해요소 리콜
          </Link>
          <Link href="/enforcement" className={navLinkClass(isActive("/enforcement"))}>
            행정처분 조회
          </Link>

          <Link href="/recalls/stats" className={navLinkClass(isActive("/recalls/stats"))}>
            식중독 통계
          </Link>
          <Link href="/analysis-chat" className={navLinkClass(isActive("/analysis-chat") || isActive("/chat"))}>
            AI 원료 분석
          </Link>
          <Link href="/regulation-chat" className={navLinkClass(isActive("/regulation-chat"))}>
            법규 채팅
          </Link>
          <Link href="/supplier" className={navLinkClass(isActive("/supplier"))}>
            납품사 조회
          </Link>

          {token ? (
            <>
              {isAdmin && (
                <Link
                  href="/admin"
                  className={cn(
                    buttonVariants({ variant: "outline", size: "sm" }),
                    isActive("/admin") && "border-primary/50 bg-primary/10 text-primary hover:text-primary",
                    "border-amber-500/30 text-amber-500 hover:bg-amber-500/10 font-medium"
                  )}
                >
                  관리자 콘솔
                </Link>
              )}
              <Link
                href="/mypage"
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  isActive("/mypage") && "border-primary/50 bg-primary/10 text-primary hover:text-primary",
                )}
              >
                마이페이지
              </Link>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleLogout}
                className="text-muted-foreground hover:text-foreground text-sm cursor-pointer"
              >
                로그아웃
              </Button>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className={cn(
                  buttonVariants({ variant: "outline", size: "sm" }),
                  isActive("/login") && "border-primary/50 bg-primary/10 text-primary hover:text-primary",
                )}
              >
                로그인
              </Link>
              <Link
                href="/signup"
                className={cn(buttonVariants({ variant: "default", size: "sm" }), "bg-primary text-primary-foreground hover:bg-primary/90")}
              >
                무료 시작하기
              </Link>
            </>
          )}
          <ThemeToggle />
          <SeoulWeatherNav />
        </div>

        <div className="flex shrink-0 items-center gap-1.5 md:hidden">
          <ThemeToggle />
          <SeoulWeatherNav />
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="shrink-0">
                <Menu className="h-5 w-5" />
                <span className="sr-only">메뉴 열기</span>
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="flex w-[min(100vw,20rem)] flex-col bg-background p-0 sm:max-w-xs">
              <SheetHeader className="sr-only">
                <SheetTitle>네비게이션 메뉴</SheetTitle>
                <SheetDescription>모바일 기기용 메인 메뉴 링크 목록입니다.</SheetDescription>
              </SheetHeader>
              <nav className="flex flex-1 flex-col gap-1 overflow-y-auto overscroll-contain px-4 pt-14 pb-8">
                <p className="mb-2 px-2 text-xs font-medium text-muted-foreground">메뉴</p>
                <Link
                  href="/recalls"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    isRecallsActive && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  위해요소 리콜
                </Link>
                <Link
                  href="/enforcement"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    isActive("/enforcement") && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  행정처분 조회
                </Link>

                <Link
                  href="/recalls/stats"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    isActive("/recalls/stats") && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  식중독 통계
                </Link>
                <Link
                  href="/analysis-chat"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    (isActive("/analysis-chat") || isActive("/chat")) && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  AI 원료 분석
                </Link>
                <Link
                  href="/regulation-chat"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    isActive("/regulation-chat") && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  법규 채팅
                </Link>
                <Link
                  href="/supplier"
                  className={cn(
                    buttonVariants({ variant: "ghost" }),
                    "h-auto min-h-10 w-full justify-start px-3 py-2.5 text-left",
                    isActive("/supplier") && "text-primary",
                  )}
                  onClick={() => setIsOpen(false)}
                >
                  납품사 조회
                </Link>



                <div className="mt-4 flex flex-col gap-2 border-t border-border/60 pt-4">
                  {token ? (
                    <>
                      {isAdmin && (
                        <Link
                          href="/admin"
                          className={cn(
                            buttonVariants({ variant: "outline" }),
                            "h-auto min-h-10 w-full justify-center border-amber-500/30 text-amber-500",
                          )}
                          onClick={() => setIsOpen(false)}
                        >
                          관리자 콘솔
                        </Link>
                      )}
                      <Link
                        href="/mypage"
                        className={cn(
                          buttonVariants({ variant: "outline" }),
                          "h-auto min-h-10 w-full justify-center",
                          isActive("/mypage") && "border-primary/50 text-primary",
                        )}
                        onClick={() => setIsOpen(false)}
                      >
                        마이페이지
                      </Link>
                      <Button
                        variant="ghost"
                        className="h-auto min-h-10 w-full justify-center text-muted-foreground hover:text-foreground"
                        onClick={() => {
                          setIsOpen(false)
                          handleLogout()
                        }}
                      >
                        로그아웃
                      </Button>
                    </>
                  ) : (
                    <>
                      <Link
                        href="/login"
                        className={cn(
                          buttonVariants({ variant: "outline" }),
                          "h-auto min-h-10 w-full justify-center",
                          isActive("/login") && "border-primary/50 text-primary",
                        )}
                        onClick={() => setIsOpen(false)}
                      >
                        로그인
                      </Link>
                      <Link
                        href="/signup"
                        className={cn(
                          buttonVariants({ variant: "default" }),
                          "h-auto min-h-10 w-full justify-center bg-primary text-primary-foreground hover:bg-primary/90",
                        )}
                        onClick={() => setIsOpen(false)}
                      >
                        무료 시작하기
                      </Link>
                    </>
                  )}
                </div>
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  )
}
