import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

type RouteContext = { params: Promise<{ path: string[] }> }

async function handleLicenseStatus(request: Request, { params }: RouteContext) {
  const { path } = await params
  const segment = path.join("/")
  return proxyToBackend({ backendPath: `/license-status/${segment}`, request })
}

export const GET = handleLicenseStatus
export const POST = handleLicenseStatus
