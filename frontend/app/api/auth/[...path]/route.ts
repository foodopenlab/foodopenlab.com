import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function handleAuth(request: Request, { params }: RouteContext) {
  const { path } = await params
  const segment = path.join("/")
  return proxyToBackend({ backendPath: `/auth/${segment}`, request })
}

export const GET = handleAuth
export const POST = handleAuth
export const PUT = handleAuth
export const PATCH = handleAuth
export const DELETE = handleAuth
