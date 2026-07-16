import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

// 크롤/스크랩은 수 초~수십 초가 걸릴 수 있어 프록시 타임아웃을 넉넉히 둔다.
export async function POST(request: Request) {
  return proxyToBackend({ backendPath: "/api/scout/run", request, timeoutMs: 120_000 })
}
