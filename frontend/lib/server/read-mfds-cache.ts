import { readFile } from "fs/promises"
import path from "path"

/** com.auditor sync가 쓰는 JSON 캐시 디렉터리 후보 (로컬 monorepo·MFDS_DATA_DIR). */
function auditorDataDirs(): string[] {
  const dirs: string[] = []
  const envDir = process.env.MFDS_DATA_DIR?.trim()
  if (envDir) dirs.push(envDir)
  dirs.push(path.join(process.cwd(), "..", "com.auditor", "apps", "mfds_user", "data"))
  dirs.push(path.join(process.cwd(), "com.auditor", "apps", "mfds_user", "data"))
  return dirs
}

/** sync catalog/scheduler가 저장한 com.auditor/apps/data/*.json 읽기. */
export async function readAuditorJsonCache<T>(filename: string): Promise<T | null> {
  for (const dir of auditorDataDirs()) {
    try {
      const raw = await readFile(path.join(dir, filename), "utf-8")
      return JSON.parse(raw) as T
    } catch {
      continue
    }
  }
  return null
}
