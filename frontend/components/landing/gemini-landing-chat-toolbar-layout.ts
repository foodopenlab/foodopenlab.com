/**
 * 랜딩 Gemini 채팅 — 입력창 아래 **한 줄 레이아웃**만 (flex·gap·margin·overflow).
 *
 * `inline-flex items-center justify-center …` 같은 값은 `@/components/ui/button`의
 * 기본 variant/size에서만 나옵니다. 여기에는 넣지 않습니다.
 */
export const geminiLandingChatToolbarRowClassName =
  "mt-3 flex min-w-0 flex-col gap-2 sm:flex-row sm:items-center sm:gap-3"

/** 왼쪽: + / 도구 묶음 */
export const geminiLandingChatToolbarLeftClassName = "flex shrink-0 items-center gap-1 sm:mr-auto"

/** 모델·음성·보내기 묶음 */
export const geminiLandingChatToolbarActionsClassName =
  "flex min-w-0 flex-wrap items-center justify-end gap-2 sm:ml-auto sm:flex-nowrap"

/** 모델 콤보 트리거 pill (레이아웃·표면색). Radix trigger 기본과 합쳐짐. */
export const geminiLandingChatModelTriggerClassName =
  "h-9 max-w-full shrink-0 gap-1 rounded-full border-border/80 bg-secondary/50 px-2.5 text-xs font-medium text-foreground hover:bg-secondary sm:px-3 [&_svg]:opacity-60"
