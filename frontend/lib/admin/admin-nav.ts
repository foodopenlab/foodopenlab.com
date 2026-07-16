import type { LucideIcon } from "lucide-react"
import {
  BarChart2,
  BookUser,
  Cpu,
  Database,
  FileText,
  GraduationCap,
  ImageUp,
  Inbox,
  LayoutDashboard,
  Mail,
  MessageCircle,
  MessageSquare,
  Radar,
  ScanFace,
  UserCheck,
} from "lucide-react"

export type AdminNavItem = {
  href: string
  label: string
  icon: LucideIcon
  /** 이 항목 위에 구분선과 섹션 제목을 표시 */
  section?: string
}

export const ADMIN_NAV_ITEMS: AdminNavItem[] = [
  { href: "/admin", label: "대시보드", icon: LayoutDashboard },
  { href: "/admin/lesson/titanic", label: "수업용", icon: GraduationCap },
  { href: "/admin/siliconvalley", label: "실리콘밸리", icon: Cpu },
  { href: "/admin/logs", label: "통합 로그", icon: FileText },
  { href: "/admin/whitelist", label: "화이트리스트", icon: UserCheck },
  { href: "/admin/api-stats", label: "API 통계", icon: BarChart2 },
  { href: "/admin/braindead/email", label: "메일 보내기", icon: Mail, section: "자동화" },
  { href: "/admin/braindead/contacts", label: "주소록", icon: BookUser },
  { href: "/admin/braindead/telegram", label: "텔레그램", icon: MessageCircle },
  { href: "/admin/braindead/discord", label: "디스코드", icon: MessageSquare },
  { href: "/admin/braindead/inbox", label: "수신함", icon: Inbox },
  { href: "/admin/vision/images", label: "이미지 업로드", icon: ImageUp, section: "비전처리" },
  { href: "/admin/vision/recognize", label: "객체탐지", icon: ScanFace },
  { href: "/admin/scout", label: "크롤러/스크래퍼", icon: Radar, section: "데이터 수집" },
  { href: "/admin/scout/results", label: "수집 결과", icon: Database },
]

export function isAdminNavActive(pathname: string | null, href: string): boolean {
  if (!pathname) return false
  if (href === "/admin") return pathname === "/admin"
  return pathname === href || pathname.startsWith(`${href}/`)
}
