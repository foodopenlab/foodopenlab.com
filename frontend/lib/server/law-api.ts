const LAW_SEARCH_URL = "https://www.law.go.kr/DRF/lawSearch.do"

const FOOD_CORE_LAW_NAMES = [
  "식품위생법",
  "식품위생법 시행령",
  "식품위생법 시행규칙",
  "축산물 위생관리법",
  "건강기능식품에 관한 법률",
  "식품 등의 표시·광고에 관한 법률",
  "식품안전기본법",
  "어린이 식생활안전관리 특별법",
]

export type LawSearchHit = {
  law_name: string
  mst: string
  article: string
  content_summary: string
  amended_date: string
  enforcement_date: string
}

function* iterRows(obj: unknown): Generator<Record<string, unknown>> {
  if (!obj || typeof obj !== "object") return
  if (Array.isArray(obj)) {
    for (const x of obj) yield* iterRows(x)
    return
  }
  const d = obj as Record<string, unknown>
  if ("법령명한글" in d || "법령명" in d || "lawNm" in d || "lsNm" in d) {
    yield d
  }
  for (const v of Object.values(d)) yield* iterRows(v)
}

function lawNameFromRow(row: Record<string, unknown>): string {
  return String(row["법령명한글"] ?? row["법령명"] ?? row.lawNm ?? row.lsNm ?? "").trim()
}

function mapRow(row: Record<string, unknown>): LawSearchHit {
  const body = String(row["조문내용"] ?? row["조문제목"] ?? row.joCnt ?? "").trim()
  return {
    law_name: lawNameFromRow(row),
    mst: String(row["법령일련번호"] ?? row["법령ID"] ?? row.MST ?? row.lsiSeq ?? "").trim(),
    article: String(row["조문번호"] ?? row["조문번호명"] ?? row.joNo ?? "").trim(),
    content_summary: body.slice(0, 200),
    amended_date: String(row["공포일자"] ?? row.promulgDate ?? "").trim(),
    enforcement_date: String(row["시행일자"] ?? row.enforcementDate ?? "").trim(),
  }
}

function filterFood(rows: Record<string, unknown>[]): Record<string, unknown>[] {
  const picked: Record<string, unknown>[] = []
  for (const r of rows) {
    const name = lawNameFromRow(r)
    if (!name) continue
    if (FOOD_CORE_LAW_NAMES.some((core) => name.includes(core) || core.includes(name))) {
      picked.push(r)
    }
  }
  return picked.length ? picked : rows
}

export function searchQueryFromMessage(message: string): string {
  const s = message.trim()
  if (!s) return ""
  const quoted = s.match(/['"]([^'"]{2,40})['"]/)
  if (quoted) return quoted[1].slice(0, 120)
  const tokens = s.match(/[가-힣a-zA-Z0-9]{2,}/g) ?? []
  if (tokens.length) {
    const longest = tokens.reduce((a, b) => (b.length > a.length ? b : a))
    if (longest.length >= 3) return longest.slice(0, 120)
  }
  return s.slice(0, 120)
}

export async function lawSearch(query: string): Promise<LawSearchHit[]> {
  const q = query.trim()
  const oc = process.env.LAW_API_KEY?.trim() ?? ""
  if (!q || !oc) return []

  const params = new URLSearchParams({
    OC: oc,
    target: "law",
    type: "JSON",
    query: q,
    display: "100",
    page: "1",
  })

  try {
    const res = await fetch(`${LAW_SEARCH_URL}?${params}`, {
      cache: "no-store",
      signal: AbortSignal.timeout(20_000),
    })
    if (!res.ok) return []
    const raw = (await res.json()) as unknown
    const candidates = [...iterRows(raw)]
    const filtered = filterFood(candidates)
    return filtered
      .map(mapRow)
      .filter((m) => m.law_name || m.mst)
      .slice(0, 3)
  } catch {
    return []
  }
}

export function formatRetrieved(items: LawSearchHit[]): string {
  if (!items.length) {
    return "(자동 조회된 조문 없음 — 일반 법규 안내로 답변하세요.)"
  }
  return items
    .map((r, i) =>
      [
        `[${i + 1}] ${r.law_name} ${r.article}`.trim(),
        `요약: ${r.content_summary}`,
        `개정일: ${r.amended_date || "-"} / 시행일: ${r.enforcement_date || "-"}`,
      ].join("\n"),
    )
    .join("\n\n")
}
