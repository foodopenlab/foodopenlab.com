"use client"

import { useEffect, useState } from "react"
import { useMyPageAuth, UserRole } from "@/hooks/use-mypage-auth"
import { Sidebar } from "@/components/mypage/sidebar"
import { Toaster } from "@/components/ui/toaster"
import { Skeleton } from "@/components/ui/skeleton"

export default function MyPageLayout({
  children,
}: {
  children: React.ReactNode
}) {
  const { token, role, isLoading: isAuthLoading, logOut } = useMyPageAuth()
  const [profileName, setProfileName] = useState<string>("")
  const [profileRole, setProfileRole] = useState<UserRole>("user")
  const [isProfileLoading, setIsProfileLoading] = useState(true)

  useEffect(() => {
    if (isAuthLoading) return
    if (!token) return

    async function fetchProfile() {
      try {
        const res = await fetch("/api/mypage/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        })

        if (res.status === 401) {
          logOut()
          return
        }

        if (res.ok) {
          const data = await res.json()
          setProfileName(data.name || "회원")
          setProfileRole(data.role || "user")
        }
      } catch (err) {
        console.error("Failed to load profile for sidebar:", err)
      } finally {
        setIsProfileLoading(false)
      }
    }

    fetchProfile()
  }, [token, isAuthLoading, logOut])

  useEffect(() => {
    const handleNameUpdate = (e: Event) => {
      const customEvent = e as CustomEvent<string>
      setProfileName(customEvent.detail)
    }
    window.addEventListener("profile-name-updated", handleNameUpdate)
    return () => {
      window.removeEventListener("profile-name-updated", handleNameUpdate)
    }
  }, [])

  const isLoading = isAuthLoading || isProfileLoading

  return (
    <div className="relative flex-1 bg-background py-8">
      {/* Decorative subtle background grid */}
      <div className="absolute inset-0 -z-10 bg-[linear-gradient(rgba(34,197,94,0.015)_1px,transparent_1px),linear-gradient(90deg,rgba(34,197,94,0.015)_1px,transparent_1px)] bg-[size:40px_40px]" />

      <div className="container mx-auto px-4 max-w-6xl">
        <div className="flex flex-col md:flex-row gap-8 items-start">
          {isLoading ? (
            // Layout Skeletons during Loading state
            <>
              <div className="w-full shrink-0 md:w-56 bg-card border border-border rounded-xl p-5 space-y-6">
                <div className="flex flex-col items-center space-y-3 pb-5 border-b border-border/60">
                  <Skeleton className="h-14 w-14 rounded-full" />
                  <Skeleton className="h-4 w-28" />
                  <Skeleton className="h-5 w-16" />
                </div>
                <div className="space-y-2">
                  <Skeleton className="h-9 w-full rounded-lg" />
                  <Skeleton className="h-9 w-full rounded-lg" />
                  <Skeleton className="h-9 w-full rounded-lg" />
                </div>
              </div>
              <div className="flex-1 w-full bg-card border border-border rounded-xl p-6 sm:p-8 space-y-6">
                <Skeleton className="h-6 w-32" />
                <div className="space-y-4">
                  <Skeleton className="h-32 w-full rounded-lg" />
                  <Skeleton className="h-20 w-full rounded-lg" />
                </div>
              </div>
            </>
          ) : (
            // Full Content Layout
            <>
              <Sidebar userName={profileName} role={profileRole} />
              <main className="flex-1 w-full min-h-[500px]">
                {children}
              </main>
            </>
          )}
        </div>
      </div>
      <Toaster />
    </div>
  )
}
