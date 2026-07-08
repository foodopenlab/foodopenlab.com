import { readAuditorJsonCache } from "@/lib/server/read-mfds-cache"
import { readJsonSnapshot } from "@/lib/server/read-snapshot"

type SanctionItem = {
  business_name: string
  industry: string
  disposition_date: string
  disposition_start?: string
  disposition_type: string
  violation: string
  address: string
  representative: string
  disposition_detail: string
  agency: string
  serial_no: string
  category: string
  service_id: string
}

type SanctionCacheFile = {
  fetched_at?: string | null
  is_today?: boolean
  matched_date?: string | null
  items?: SanctionItem[]
}

type Snapshot = SanctionCacheFile

function kstTodayIso(): string {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Asia/Seoul" }).format(new Date())
}

function normalizeSanctionItems(raw: SanctionItem[] | undefined): SanctionItem[] {
  return (raw ?? []).filter((item) => Boolean(item.business_name?.trim()))
}

function responseFromCache(
  cache: SanctionCacheFile,
  query_date: string,
): {
  items: SanctionItem[]
  fetched_at: string | null
  query_date: string
  is_today: boolean
  matched_date: string | null
  source: string
} {
  const items = normalizeSanctionItems(cache.items).slice(0, 1)
  return {
    items,
    fetched_at: cache.fetched_at ?? null,
    query_date,
    is_today: Boolean(cache.is_today),
    matched_date: cache.matched_date ?? null,
    source: "식품안전나라",
  }
}

async function fetchBackendLatestSanctions(query_date: string) {
  const backend = (process.env.BACKEND_URL || process.env.NEXT_PUBLIC_API_URL || "").trim()
  if (!backend) return null

  const origin = backend.replace(/\/$/, "")
  const res = await fetch(`${origin}/sanctions/latest`, {
    cache: "no-store",
    signal: AbortSignal.timeout(15_000),
  })
  if (!res.ok) return null

  const body = (await res.json()) as SanctionCacheFile & {
    query_date?: string
    source?: string
  }
  if (!normalizeSanctionItems(body.items).length) return null

  return {
    items: normalizeSanctionItems(body.items).slice(0, 1),
    fetched_at: body.fetched_at ?? null,
    query_date,
    is_today: Boolean(body.is_today),
    matched_date: body.matched_date ?? null,
    source: body.source ?? "식품안전나라",
  }
}

/** 메인 카드용 — sync가 갱신한 sanction_cache.json 우선 (로컬), 배포 시 백엔드 /sanctions/latest 폴백. */
export async function getLatestSanctionsResponse() {
  const query_date = kstTodayIso()

  const cache = await readAuditorJsonCache<SanctionCacheFile>("sanction_cache.json")
  if (cache && normalizeSanctionItems(cache.items).length) {
    return responseFromCache(cache, query_date)
  }

  try {
    const fromBackend = await fetchBackendLatestSanctions(query_date)
    if (fromBackend) return fromBackend
  } catch {
    /* snapshot fallback */
  }

  const snap = await readJsonSnapshot<Snapshot>("sanction_snapshot.json")
  if (snap && normalizeSanctionItems(snap.items).length) {
    return responseFromCache(snap, query_date)
  }

  return {
    items: [],
    fetched_at: null,
    query_date,
    is_today: false,
    matched_date: null,
    source: "식품안전나라",
  }
}
