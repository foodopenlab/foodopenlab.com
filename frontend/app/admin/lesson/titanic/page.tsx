import { CsvUploadSection } from "@/components/titanic/csv-upload-section"

export default function TitanicLessonPage() {
  return (
    <div className="container mx-auto flex max-w-6xl flex-col gap-8 px-4 py-10">
      <div className="space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">TITANIC DATASET · STEP 1</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">1. 데이터수집</h1>
        <p className="mx-auto max-w-2xl text-sm text-muted-foreground sm:text-base">
          타이타닉 CSV 데이터를 업로드해 이후 분석 단계를 준비합니다.
        </p>
      </div>
      <div className="mx-auto w-full">
        <CsvUploadSection />
      </div>
    </div>
  )
}
