import { dirname } from "path"
import { fileURLToPath } from "url"

import { resolveBackendOrigin } from "./lib/backend-origin.mjs"

const projectRoot = dirname(fileURLToPath(import.meta.url))

/** @type {import('next').NextConfig} */
const nextConfig = {
  // 모노레포(com.foodopenlab) 안에서 Next가 상위 폴더를 루트로 잡아
  // node_modules/next 를 못 찾거나 파일 트레이싱 루트가 어긋나는 것을 막는다.
  // turbopack.root 와 반드시 같은 값이어야 한다(다르면 빌드 경고).
  outputFileTracingRoot: projectRoot,
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
