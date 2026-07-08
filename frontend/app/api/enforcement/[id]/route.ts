import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ id: string }> }

export async function GET(request: Request, { params }: RouteContext) {
  const { id } = await params
  return proxyToBackend({ backendPath: `/enforcement/${encodeURIComponent(id)}`, request })
}
