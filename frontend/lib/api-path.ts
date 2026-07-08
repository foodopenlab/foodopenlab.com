/**
 * 브라우저에서 호출하는 API 경로.
 * 항상 같은 오리진의 `/api/*`만 사용합니다 (Vercel이 `next.config` rewrite로 백엔드에 연결).
 * `NEXT_PUBLIC_API_URL=http://127.0.0.1:8000`처럼 공개 URL에 사설 IP를 넣으면
 * `DNS_HOSTNAME_RESOLVED_PRIVATE` 오류가 납니다.
 */
export function apiPath(route: string): string {
  const normalized = route.replace(/^\//, "")
  return `/api/${normalized}`
}

/** Titanic CSV — 로컬 dev는 Next 프록시 대신 FastAPI(8000) 직접 호출(멈춤 방지). */
export function titanicUploadUrl(): string {
  if (typeof window !== "undefined" && process.env.NODE_ENV === "development") {
    const origin = (process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000").replace(/\/$/, "")
    return `${origin}/api/titanic/james/upload`
  }
  return apiPath("lesson/titanic/james/upload")
}

/** fetch 실패·Vercel 프록시 오류 메시지를 사용자용 문구로 정리 */
export function formatApiClientError(message: string): string {
  if (message.includes("Tunnel Unavailable") || message.includes("503 - Tunnel")) {
    return (
      "백엔드 터널(ngrok 등)에 연결할 수 없습니다. Vercel의 BACKEND_URL을 삭제하거나, " +
      "공개 FastAPI 서버 URL만 설정하세요. 회수·통계·채팅은 Vercel API 라우트로도 동작합니다."
    )
  }
  if (message.includes("DNS_HOSTNAME_NOT_FOUND")) {
    return (
      "백엔드 주소(BACKEND_URL)의 도메인을 찾을 수 없습니다. " +
      "Vercel에 설정한 URL이 실제로 DNS·서버에 연결돼 있는지 확인하세요. " +
      "백엔드가 아직 없으면 BACKEND_URL을 비우고 재배포한 뒤, 공개 API가 준비되면 다시 넣으세요."
    )
  }
  if (message.includes("DNS_HOSTNAME_RESOLVED_PRIVATE")) {
    return (
      "배포 서버가 로컬 주소(127.0.0.1)로 API를 호출할 수 없습니다. " +
      "Vercel 환경 변수 BACKEND_URL에 공개 HTTPS API 주소를 설정하고, NEXT_PUBLIC_API_URL=127.0.0.1 은 제거한 뒤 재배포해 주세요."
    )
  }
  if (message.includes("429") || message.toLowerCase().includes("quota")) {
    return "Gemini API 할당량 초과입니다. Google AI Studio에서 키·사용량을 확인해 주세요."
  }
  if (message.includes("An error occurred with this application") && message.includes("DNS_")) {
    if (message.includes("NOT_FOUND")) {
      return formatApiClientError("DNS_HOSTNAME_NOT_FOUND")
    }
    return formatApiClientError("DNS_HOSTNAME_RESOLVED_PRIVATE")
  }
  if (message.includes("The page could not be found") && message.includes("DNS_")) {
    return formatApiClientError(
      message.includes("NOT_FOUND") ? "DNS_HOSTNAME_NOT_FOUND" : "DNS_HOSTNAME_RESOLVED_PRIVATE",
    )
  }
  return message
}
