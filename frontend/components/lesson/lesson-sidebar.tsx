"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Anchor, BookOpen, Menu } from "lucide-react"

import { Button, buttonVariants } from "@/components/ui/button"
import { Sheet, SheetContent, SheetTrigger, SheetHeader, SheetTitle, SheetDescription } from "@/components/ui/sheet"
import { cn } from "@/lib/utils"

export const LESSON_SIDEBAR_WIDTH_CLASS = "w-56"

const LESSON_TITANIC_STEPS = [
  {
    href: "/admin/lesson/titanic",
    label: "1. 데이터수집",
    description: "CSV 업로드 · 데이터 분석",
  },
  {
    href: "/admin/lesson/titanic/view",
    label: "2. 탑승자 목록",
    description: "월터 로스터 소개",
  },
  {
    href: "/admin/lesson/titanic/smith",
    label: "3. 스미스 선장",
    description: "스미스 선장과 대화",
  },
]

function SidebarPanel({ className, onNavigate }: { className?: string; onNavigate?: () => void }) {
  const pathname = usePathname()
  const lessonHomeActive = pathname === "/admin/lesson"
  const titanicActive = pathname === "/admin/lesson/titanic" || pathname?.startsWith("/admin/lesson/titanic/")

  return (
    <aside
      className={cn(
        "flex flex-col rounded-2xl border border-border/80 bg-card/95",
        LESSON_SIDEBAR_WIDTH_CLASS,
        className,
      )}
    >
      <div className="px-4 py-4">
        <Link
          href="/admin/lesson"
          onClick={onNavigate}
          className={cn(
            "mb-3 flex items-center gap-1.5 text-xs font-medium transition-colors",
            lessonHomeActive ? "text-primary" : "text-muted-foreground hover:text-foreground",
          )}
        >
          <BookOpen className="h-3.5 w-3.5 shrink-0" aria-hidden />
          수업용
        </Link>
        <div
          className={cn(
            "flex items-center gap-2 rounded-md px-2 py-2 text-base font-semibold",
            titanicActive ? "text-primary" : "text-foreground",
          )}
        >
          <Anchor className="h-4 w-4 shrink-0" aria-hidden />
          타이타닉
        </div>
        <nav className="mt-1 space-y-1 pl-6" aria-label="타이타닉 수업 단계">
          {LESSON_TITANIC_STEPS.map((step) => {
            const active = pathname === step.href
            return (
              <Link
                key={step.href}
                href={step.href}
                onClick={onNavigate}
                aria-current={active ? "page" : undefined}
                className={cn(
                  buttonVariants({ variant: "ghost", size: "sm" }),
                  "h-auto min-h-9 w-full flex-col items-start justify-center gap-0 px-2 py-1.5 text-left",
                  active && "bg-primary/10 text-primary hover:text-primary",
                )}
              >
                <span className="text-sm font-semibold">{step.label}</span>
                <span className="text-[11px] text-muted-foreground">{step.description}</span>
              </Link>
            )
          })}
        </nav>
      </div>
    </aside>
  )
}

/** 데스크톱: 관리자 본문 영역에 나란히 배치되는 사이드바 */
export function LessonSidebarDesktop() {
  return <SidebarPanel className="hidden shrink-0 lg:flex" />
}

/** 모바일: 본문 상단 메뉴 바 */
export function LessonSidebarMobile() {
  return (
    <div className="flex shrink-0 items-center gap-2 pb-3 lg:hidden">
      <Sheet>
        <SheetTrigger asChild>
          <Button type="button" variant="outline" size="icon" aria-label="수업용 메뉴">
            <Menu className="h-5 w-5" />
          </Button>
        </SheetTrigger>
        <SheetContent side="left" className="w-64 p-0">
          <SheetHeader className="sr-only">
            <SheetTitle>수업용 메뉴 사이드바</SheetTitle>
            <SheetDescription>수업용 페이지들을 이동할 수 있는 보조 메뉴판입니다.</SheetDescription>
          </SheetHeader>
          <SidebarPanel
            className="flex h-full w-full rounded-none border-0"
            onNavigate={() => {
              document.querySelector<HTMLButtonElement>('[data-slot="sheet-close"]')?.click()
            }}
          />
        </SheetContent>
      </Sheet>
      <span className="text-sm font-semibold text-foreground">타이타닉 수업</span>
    </div>
  )
}

export function LessonSidebar() {
  return (
    <>
      <LessonSidebarMobile />
      <LessonSidebarDesktop />
    </>
  )
}
