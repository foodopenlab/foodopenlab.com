import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function handlePiper(request: Request, { params }: RouteContext) {
  const { path } = await params
  const segment = path.join("/")
  return proxyToBackend({ backendPath: `/api/piper/${segment}`, request })
}

export const GET = handlePiper
export const POST = handlePiper
export const PUT = handlePiper
export const PATCH = handlePiper
export const DELETE = handlePiper
