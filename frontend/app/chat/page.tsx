import { redirect } from "next/navigation"

/** 하위 호환 — `/analysis-chat` 으로 이동 */
export default function ChatLegacyRedirect() {
  redirect("/analysis-chat")
}
