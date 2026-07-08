const PIPER_CHARACTERS = [
  { key: "bighetti", label: "Bighetti HR", role: "HR", route: "/api/piper/bighetti/myself" },
  { key: "dinesh", label: "Dinesh Dash", role: "대시보드", route: "/api/piper/dinesh/myself" },
  { key: "dunn", label: "Dunn COO", role: "COO", route: "/api/piper/dunn/myself" },
  { key: "gilfoyle", label: "Gilfoyle Sys", role: "시스템", route: "/api/piper/gilfoyle/myself" },
  { key: "hendricks", label: "Hendricks CEO", role: "CEO", route: "/api/piper/hendricks/myself" },
] as const

export type PiperCharacterKey = (typeof PIPER_CHARACTERS)[number]["key"]

export type PiperMyselfResponse = {
  id: number
  name: string
}

export type PiperCharacterStatus = {
  key: PiperCharacterKey
  label: string
  role: string
  online: boolean
  id?: number
  name?: string
  error?: string
}

export async function fetchPiperStatuses(): Promise<PiperCharacterStatus[]> {
  const results = await Promise.all(
    PIPER_CHARACTERS.map(async (character) => {
      try {
        const res = await fetch(character.route, { cache: "no-store" })
        if (!res.ok) {
          return {
            key: character.key,
            label: character.label,
            role: character.role,
            online: false,
            error: `HTTP ${res.status}`,
          }
        }
        const data = (await res.json()) as PiperMyselfResponse
        return {
          key: character.key,
          label: character.label,
          role: character.role,
          online: true,
          id: data.id,
          name: data.name,
        }
      } catch (e) {
        return {
          key: character.key,
          label: character.label,
          role: character.role,
          online: false,
          error: e instanceof Error ? e.message : "요청 실패",
        }
      }
    }),
  )
  return results
}

export { PIPER_CHARACTERS }
