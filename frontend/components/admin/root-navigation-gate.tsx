"use client"

import { usePathname } from "next/navigation"
import { Navigation } from "@/components/landing/navigation"

/** `/admin` 구간에서는 루트 랜딩 Navbar를 숨깁니다. */
export function RootNavigationGate() {
  const pathname = usePathname()
  if (pathname?.startsWith("/admin")) return null
  return <Navigation />
}
