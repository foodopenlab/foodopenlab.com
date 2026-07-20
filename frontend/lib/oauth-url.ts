// 소셜 로그인 시작 URL — 백엔드로 직접 top-level 이동해야 302 리다이렉트 체인이 정상 동작한다.
// (Next 프록시를 거치면 서버가 리다이렉트를 삼켜버림)

export type SocialProvider = "google" | "kakao" | "naver"

export function socialLoginUrl(provider: SocialProvider): string {
  const base = (process.env.NEXT_PUBLIC_API_URL ?? "").replace(/\/$/, "")
  return `${base}/auth/${provider}/login`
}
