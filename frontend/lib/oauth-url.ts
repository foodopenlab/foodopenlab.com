// 소셜 로그인 시작 URL — 백엔드로 top-level 이동해야 302 리다이렉트 체인이 정상 동작한다.
// 로컬: NEXT_PUBLIC_API_URL(백엔드)로 직접. 프로덕션: 이 변수가 비므로 같은 오리진
// /api/auth/* 로 이동해 next.config.mjs rewrite가 백엔드로 프록시한다(다른 API와 동일 패턴).

export type SocialProvider = "google" | "kakao" | "naver"

export function socialLoginUrl(provider: SocialProvider): string {
  // 로그인은 auth 게이트웨이(RS256)로 통합. 콜백은 auth가 프론트 /auth/callback#토큰 으로 리다이렉트.
  const base = (process.env.NEXT_PUBLIC_AUTH_URL || "https://auth.foodopenlab.com").replace(/\/$/, "")
  return `${base}/auth/${provider}/login`
}
