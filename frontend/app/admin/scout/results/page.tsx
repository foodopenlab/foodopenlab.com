import { ScoutResults } from "@/components/admin/scout/scout-results"

export default function AdminScoutResultsPage() {
  return (
    <div className="container mx-auto max-w-5xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">DATA · RESULTS</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">수집 결과</h1>
        <p className="mx-auto max-w-xl text-sm text-muted-foreground sm:text-base">
          resources에 저장된 크롤러·스크래퍼 결과를 조회합니다. 확인·필터링 후 Redis에 적재하세요.
        </p>
      </div>
      <ScoutResults />
    </div>
  )
}
