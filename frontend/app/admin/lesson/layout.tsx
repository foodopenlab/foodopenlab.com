import type { ReactNode } from "react"

import { LessonSidebarDesktop, LessonSidebarMobile } from "@/components/lesson/lesson-sidebar"

/** 관리자 본문 영역 안에 사이드바 + 콘텐츠를 나란히 배치 */
export default function LessonLayout({ children }: { children: ReactNode }) {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <LessonSidebarMobile />
      <div className="flex min-h-0 flex-1 flex-col gap-4 lg:flex-row lg:gap-6">
        <LessonSidebarDesktop />
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </div>
  )
}
