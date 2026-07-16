import { proxyToBackend } from "@/lib/server/backend-proxy"

export const dynamic = "force-dynamic"

// proxyToBackend가 요청의 쿼리스트링(?kind=&limit=)을 그대로 백엔드에 붙여준다.
export async function GET(request: Request) {
  return proxyToBackend({ backendPath: "/api/scout/results", request })
}
