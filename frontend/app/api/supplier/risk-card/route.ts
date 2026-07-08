import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

export async function GET(request: Request) {
  return proxyToBackend({ backendPath: "/supplier/risk-card", request, timeoutMs: 20_000 })
}
