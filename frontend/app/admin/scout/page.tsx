import { ScoutConsole } from "@/components/admin/scout/scout-console"

export default function AdminScoutPage() {
  return (
    <div className="container mx-auto max-w-2xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">DATA · SCOUT</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">크롤러/스크래퍼</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          사이트 주소와 자연어 명령을 입력하면 AI가 명령을 이해해 크롤링·스크래핑을 실행합니다.
        </p>
      </div>
      <ScoutConsole />
    </div>
  )
}
