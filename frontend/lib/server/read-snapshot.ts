import { readFile } from "fs/promises"
import path from "path"

export async function readJsonSnapshot<T>(filename: string): Promise<T | null> {
  try {
    const filePath = path.join(process.cwd(), "data", filename)
    const raw = await readFile(filePath, "utf-8")
    return JSON.parse(raw) as T
  } catch {
    return null
  }
}
