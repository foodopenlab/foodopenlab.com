/** `/lesson` 기본 화면 — 가운데 「수업용」만 표시 */
export function LessonHomePlaceholder() {
  return (
    <div className="flex flex-1 items-center justify-center px-4 py-16">
      <p className="text-balance text-center text-4xl font-bold tracking-tight text-foreground/90 sm:text-5xl md:text-6xl">
        수업용
      </p>
    </div>
  )
}
