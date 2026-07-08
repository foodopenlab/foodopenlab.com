"use client"

import { useEffect, useState, useCallback } from "react"
import { useRouter } from "next/navigation"

export type UserRole = "user" | "expert"

export interface DecodedUser {
  userId: number
  email: string
  role: UserRole
  name?: string
}

export function useMyPageAuth() {
  const router = useRouter()
  const [token, setToken] = useState<string | null>(null)
  const [userId, setUserId] = useState<number | null>(null)
  const [role, setRole] = useState<UserRole | null>(null)
  const [email, setEmail] = useState<string>("")
  const [isLoading, setIsLoading] = useState(true)

  const logOut = useCallback(() => {
    localStorage.removeItem("access_token")
    setToken(null)
    setUserId(null)
    setRole(null)
    setEmail("")
    router.push("/login")
  }, [router])

  useEffect(() => {
    const storedToken = localStorage.getItem("access_token")

    if (!storedToken) {
      setIsLoading(false)
      router.push("/login")
      return
    }

    try {
      const parts = storedToken.split(".")
      if (parts.length !== 3) {
        throw new Error("Invalid token format")
      }

      // Safe base64 decoding supporting UTF-8 characters
      const base64Url = parts[1]
      const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/")
      const jsonPayload = decodeURIComponent(
        atob(base64)
          .split("")
          .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
          .join("")
      )
      const payload = JSON.parse(jsonPayload)

      if (!payload.sub || !payload.role) {
        throw new Error("Missing critical claims in token payload")
      }

      // Check token expiration (if exp is present)
      if (payload.exp && payload.exp * 1000 < Date.now()) {
        localStorage.removeItem("access_token")
        router.push("/login")
        return
      }

      setToken(storedToken)
      setUserId(parseInt(payload.sub, 10))
      setRole(payload.role as UserRole)
      setEmail(payload.email || "")
    } catch (err) {
      console.error("Token decoding failed:", err)
      localStorage.removeItem("access_token")
      router.push("/login")
    } finally {
      setIsLoading(false)
    }
  }, [router])

  return { token, userId, role, email, isLoading, logOut }
}
