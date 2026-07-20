// 소셜 로그인 provider 아이콘 (단색, currentColor로 버튼 text 색상 상속)

export function KakaoIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M12 0C5.373 0 0 4.184 0 9.286c0 3.298 2.246 6.19 5.625 7.815-.184.665-.994 3.6-1.02 3.836 0 0-.02.174.092.24.113.067.24.014.24.014.312-.043 3.617-2.365 4.191-2.766.594.085 1.207.13 1.872.13 6.627 0 12-4.184 12-9.286C24 4.184 18.627 0 12 0" />
    </svg>
  )
}

export function NaverIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor" aria-hidden>
      <path d="M16.273 12.845 7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845Z" />
    </svg>
  )
}
