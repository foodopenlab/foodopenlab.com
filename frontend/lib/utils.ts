import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** 회수·행정처분 일자 문자열 → YYYY-MM-DD (20260520, ISO·시간 포함 모두 처리) */
export function formatRegisteredDate(value: string | null | undefined): string {
  const raw = (value ?? "").trim()
  if (!raw) return ""
  const head = raw.split(/[T\s]/)[0] ?? raw
  if (/^\d{4}-\d{2}-\d{2}$/.test(head)) return head
  const digits = head.replace(/\D/g, "")
  if (digits.length >= 8) {
    return `${digits.slice(0, 4)}-${digits.slice(4, 6)}-${digits.slice(6, 8)}`
  }
  return head.length >= 10 ? head.slice(0, 10) : head
}
