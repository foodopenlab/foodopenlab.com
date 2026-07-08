"use client"

import { useEffect, useState } from "react"
import { useMyPageAuth, UserRole } from "@/hooks/use-mypage-auth"
import { InlineNameEditor } from "@/components/mypage/inline-name-editor"
import { ProfileInfoCard } from "@/components/mypage/profile-info-card"
import { Skeleton } from "@/components/ui/skeleton"

interface ProfileData {
  id: number
  email: string
  name: string
  role: UserRole
  is_active: boolean
  last_login_at: string | null
  created_at: string
}

export default function BasicInfoPage() {
  const { token, isLoading: isAuthLoading } = useMyPageAuth()
  const [profile, setProfile] = useState<ProfileData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isAuthLoading) return
    if (!token) return

    async function fetchProfile() {
      try {
        setIsLoading(true)
        const res = await fetch("/api/mypage/profile", {
          headers: {
            Authorization: `Bearer ${token}`,
            Accept: "application/json",
          },
        })

        if (!res.ok) {
          throw new Error("Failed to load profile details")
        }

        const data = await res.json()
        setProfile(data)
      } catch (err) {
        console.error(err)
        setError("기본 정보를 불러오는 데 실패했습니다.")
      } finally {
        setIsLoading(false)
      }
    }

    fetchProfile()
  }, [token, isAuthLoading])

  const handleNameUpdated = (newName: string) => {
    if (profile) {
      setProfile({ ...profile, name: newName })
      // Dispatch event to update the sidebar name in MyPageLayout
      window.dispatchEvent(new CustomEvent("profile-name-updated", { detail: newName }))
    }
  }

  if (isAuthLoading || isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <Skeleton className="h-8 w-32 mb-2" />
          <Skeleton className="h-4 w-64" />
        </div>
        <Skeleton className="h-32 w-full rounded-xl" />
        <Skeleton className="h-48 w-full rounded-xl" />
      </div>
    )
  }

  if (error || !profile) {
    return (
      <div className="flex flex-col items-center justify-center p-8 bg-card border border-border rounded-xl shadow-sm text-center">
        <p className="text-destructive font-medium">{error || "사용자 프로필을 찾을 수 없습니다."}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl font-bold text-foreground">기본 정보</h1>
        <p className="text-sm text-muted-foreground">회원님의 기본 프로필을 확인하고 이름을 수정할 수 있습니다.</p>
      </div>

      {/* Inline Name Editor */}
      <InlineNameEditor
        initialName={profile.name}
        token={token!}
        onNameUpdated={handleNameUpdated}
      />

      {/* Read-Only Account Details */}
      <ProfileInfoCard
        email={profile.email}
        role={profile.role}
        createdAt={profile.created_at}
        lastLoginAt={profile.last_login_at}
      />
    </div>
  )
}
