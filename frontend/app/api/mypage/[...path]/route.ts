import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function handleMypage(request: Request, { params }: RouteContext) {
  const { path } = await params
  const segment = path.join("/")
  return proxyToBackend({ backendPath: `/mypage/${segment}`, request })
}

export const GET = handleMypage
export const POST = handleMypage
export const PUT = handleMypage
export const PATCH = handleMypage
export const DELETE = handleMypage
