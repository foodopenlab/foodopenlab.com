import type { ReactNode } from "react"

const LINK_CLASS =
  "text-primary hover:text-primary/80 underline font-semibold transition-all break-all inline"

/** URL 끝에 붙은 문장 부호 제거 */
function trimTrailingPunctuation(url: string): string {
  return url.replace(/[.,;:!?)\]}>]+$/g, "")
}

function toHref(raw: string): string {
  const u = trimTrailingPunctuation(raw)
  if (/^https?:\/\//i.test(u)) return u
  if (/^www\./i.test(u)) return `https://${u}`
  return `https://${u}`
}

type Segment = { type: "text"; value: string } | { type: "link"; label: string; href: string }

/**
 * 마크다운 [텍스트](https://...) · https:// · www. 도메인을 링크로 분리
 */
function splitIntoSegments(content: string): Segment[] {
  const re =
    /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)|(https?:\/\/[^\s)<>\]]+)|(www\.[a-zA-Z0-9][-a-zA-Z0-9.]*\.[a-zA-Z]{2,}(?:\/[^\s)<>\]]*)?)/gi

  const segments: Segment[] = []
  let lastIndex = 0
  let match: RegExpExecArray | null

  while ((match = re.exec(content)) !== null) {
    const idx = match.index
    if (idx > lastIndex) {
      segments.push({ type: "text", value: content.slice(lastIndex, idx) })
    }

    if (match[1] && match[2]) {
      segments.push({ type: "link", label: match[1], href: trimTrailingPunctuation(match[2]) })
    } else if (match[3]) {
      const url = trimTrailingPunctuation(match[3])
      segments.push({ type: "link", label: url, href: url })
    } else if (match[4]) {
      const url = trimTrailingPunctuation(match[4])
      segments.push({ type: "link", label: url, href: toHref(url) })
    }

    lastIndex = re.lastIndex
  }

  if (lastIndex < content.length) {
    segments.push({ type: "text", value: content.slice(lastIndex) })
  }

  return segments.length ? segments : [{ type: "text", value: content }]
}

export function renderChatMessageContent(content: string): ReactNode {
  if (!content) return null

  const segments = splitIntoSegments(content)
  const nodes: ReactNode[] = []

  segments.forEach((seg, i) => {
    if (seg.type === "text") {
      nodes.push(<span key={`t-${i}`}>{seg.value}</span>)
      return
    }
    nodes.push(
      <a
        key={`l-${i}-${seg.href}`}
        href={seg.href}
        target="_blank"
        rel="noopener noreferrer"
        className={LINK_CLASS}
      >
        {seg.label}
      </a>,
    )
  })

  return <>{nodes}</>
}

/** AI 원료 분석·법규 채팅 공통 시스템 지침 (백엔드 chat_service / regulation_service 와 동일) */
export const ANALYSIS_CHAT_SYSTEM_PROMPT = `당신은 식품 위해·HACCP·원료 규격 관련 안내를 돕는 한국어 어시스턴트입니다.
답변은 핵심 위주로 간결하게(글머리 기호) 작성하세요.
필요한 경우 답변 본문이나 하단에 공공기관 출처를 마크다운 하이퍼링크로 남겨주세요.
복잡한 하위 URL은 만들지 말고 공식 홈페이지 메인 주소만 링크하세요.
반드시 [식품안전나라](https://www.foodsafetykorea.go.kr) 처럼 대괄호와 소괄호 사이에 공백 없이 작성하세요.
괄호 안에 메뉴 경로만 텍스트로 안내할 수 있습니다. 예: [식품안전나라](https://www.foodsafetykorea.go.kr) (위해·예방 > 회수·판매중지)
www.foodsafetykorea.go.kr 만 단독으로 쓰지 말고 위 마크다운 링크 형식을 사용하세요.
확실하지 않은 내용은 추측하지 말고, 공공 데이터·전문가 확인을 안내하세요.`
