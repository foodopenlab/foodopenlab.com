/**
 * 랜딩 툴바의 **아이콘 버튼에만** 덧씌우는 크롬.
 * 긴 공통 문자열(`inline-flex` … `focus-visible:ring-[3px]` 등)은 전부
 * `Button`의 `buttonVariants`에서만 붙습니다 — 이 파일에는 없습니다.
 */
export const geminiLandingChatToolbarIconButtonChrome =
  "h-9 w-9 shrink-0 rounded-full"

/** 보내기: `variant="default"`일 때 덮어쓰는 톤 */
export const geminiLandingChatToolbarSendReadyChrome =
  "border-transparent bg-primary text-primary-foreground hover:bg-primary/90"

/** 보내기: `variant="outline"` + 입력 없음일 때 */
export const geminiLandingChatToolbarSendIdleChrome =
  "border-border text-muted-foreground hover:bg-secondary hover:text-foreground"

/** 마이크 버튼 (ghost + 크기) */
export const geminiLandingChatToolbarVoiceChrome =
  `${geminiLandingChatToolbarIconButtonChrome} text-foreground hover:bg-accent hover:text-foreground`
