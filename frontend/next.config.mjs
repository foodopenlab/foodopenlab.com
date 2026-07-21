import { dirname } from "path"
import { fileURLToPath } from "url"

import { resolveBackendOrigin } from "./lib/backend-origin.mjs"

const projectRoot = dirname(fileURLToPath(import.meta.url))

// CSP는 우리가 쓰는 리소스(Next 인라인 부트스트랩, 폰트/이미지, 구글 OAuth 이동, api 호출)를
// 깨지 않도록 처음엔 Report-Only(차단 없이 콘솔 경고만)로 깔고, 위반을 보며 조인 뒤 enforce로 승격한다.
const CONTENT_SECURITY_POLICY = [
  "default-src 'self'",
  "script-src 'self' 'unsafe-inline' 'unsafe-eval'",
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob: https:",
  "font-src 'self' data:",
  "connect-src 'self' https://api.foodopenlab.com",
  "frame-ancestors 'none'",
  "base-uri 'self'",
  "form-action 'self' https://api.foodopenlab.com",
].join("; ")

const SECURITY_HEADERS = [
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  { key: "Strict-Transport-Security", value: "max-age=63072000; includeSubDomains; preload" },
  { key: "Content-Security-Policy-Report-Only", value: CONTENT_SECURITY_POLICY },
]

/** @type {import('next').NextConfig} */
const nextConfig = {
  poweredByHeader: false,
  async headers() {
    return [{ source: "/:path*", headers: SECURITY_HEADERS }]
  },
  // 모노레포(com.foodopenlab) 안에서 Turbopack이 상위 폴더를 루트로 잡아
  // node_modules/next 를 못 찾는 패닉 방지.
  // 주의: outputFileTracingRoot 는 여기서 설정하지 않는다 — Vercel(Root Directory=frontend)이
  // 모노레포 루트 기준으로 트레이싱하므로, frontend로 강제하면 onBuildComplete가
  // .next 매니페스트를 레포 루트에서 못 찾아 ENOENT 로 실패한다("Both ... same value" 경고는 무해).
  turbopack: {
    root: projectRoot,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    unoptimized: true,
  },
  async rewrites() {
    const apiOrigin = resolveBackendOrigin()
    if (!apiOrigin) return []

    return [
      // FastAPI: /api/lesson/titanic/* (james/upload 는 app/api/.../route.ts 가 우선)
      { source: "/api/lesson/titanic/:path*", destination: `${apiOrigin}/api/titanic/:path*` },
      { source: "/api/piper/:path*", destination: `${apiOrigin}/api/piper/:path*` },
      { source: "/api/haccp-cert/:path*", destination: `${apiOrigin}/haccp-cert/:path*` },
      // /api/admin/* 는 app/api/admin/[...path]/route.ts(동적 라우트)가 처리 — rewrites 배열은
      // 동적 라우트보다 먼저 적용돼 이 규칙이 있으면 route.ts가 절대 실행되지 않음
      { source: "/api/auth/:path*", destination: `${apiOrigin}/auth/:path*` },
      { source: "/api/mypage/:path*", destination: `${apiOrigin}/mypage/:path*` },
      { source: "/api/food-stats/:path*", destination: `${apiOrigin}/food-stats/:path*` },
      { source: "/api/enforcement", destination: `${apiOrigin}/enforcement` },
      { source: "/api/enforcement/:path*", destination: `${apiOrigin}/enforcement/:path*` },
      { source: "/api/license-status", destination: `${apiOrigin}/license-status` },
      { source: "/api/license-status/:path*", destination: `${apiOrigin}/license-status/:path*` },
      { source: "/api/supplier/risk-card", destination: `${apiOrigin}/supplier/risk-card` },
    ]
  },
}

export default nextConfig
