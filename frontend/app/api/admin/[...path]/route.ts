import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function handleAdmin(request: Request, { params }: RouteContext) {
  const { path } = await params
  if (path[0] === "braindead") {
    return proxyToBackend({ backendPath: `/api/braindead/${path.slice(1).join("/")}`, request })
  }
  const segment = path.join("/")
  return proxyToBackend({ backendPath: `/admin/${segment}`, request })
}

export const GET = handleAdmin
export const POST = handleAdmin
export const PUT = handleAdmin
export const PATCH = handleAdmin
export const DELETE = handleAdmin
