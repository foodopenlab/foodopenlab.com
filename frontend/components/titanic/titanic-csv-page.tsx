import Image from "next/image"

import { CsvUploadSection } from "@/components/titanic/csv-upload-section"

/** 타이타닉 CSV 업로드 풀페이지 (배경·히어로·업로드 섹션) */
export function TitanicCsvPage() {
  return (
    <div className="relative flex min-h-0 flex-1 flex-col overflow-hidden bg-background">
      <div className="pointer-events-none absolute inset-0">
        <Image
          src="/titanic/hero-bg.png"
          alt=""
          fill
          className="object-cover object-[50%_10%] opacity-90 md:object-[48%_8%]"
          sizes="100vw"
          priority
        />
      </div>

      <div
        aria-hidden
        className="pointer-events-none absolute inset-0"
        style={{
          background: [
            "linear-gradient(155deg, oklch(0.04 0.03 250 / 0.88) 0%, transparent 42%, oklch(0.03 0.03 250 / 0.75) 100%)",
            "linear-gradient(to bottom, oklch(0.02 0.02 250 / 0.65) 0%, oklch(0.06 0.04 250 / 0.2) 45%, oklch(0.02 0.02 250 / 0.92) 100%)",
            "radial-gradient(ellipse 90% 55% at 72% 88%, oklch(0.62 0.12 75 / 0.18), transparent 58%)",
            "radial-gradient(ellipse 55% 45% at 18% 55%, oklch(0.72 0.17 160 / 0.1), transparent 52%)",
          ].join(","),
        }}
      />

      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            "linear-gradient(rgba(34,197,94,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(34,197,94,0.05)_1px,transparent_1px)",
          backgroundSize: "48px 48px",
        }}
      />

      <main className="relative z-10 flex flex-1 flex-col items-center gap-10 px-4 py-10 md:gap-12 md:py-16">
        <div className="flex flex-col items-center gap-3 text-center">
          <p className="text-xs font-medium uppercase tracking-[0.2em] text-amber-100/80">Titanic dataset · Step 1</p>
          <h1 className="max-w-3xl text-balance text-4xl font-bold tracking-tight text-white drop-shadow-[0_2px_24px_rgba(0,0,0,0.85)] md:text-6xl">
            1. <span className="text-primary">데이터수집</span>
          </h1>
          <p className="max-w-md text-sm text-white/75 md:text-base">
            타이타닉 CSV 데이터를 업로드해 이후 분석 단계를 준비합니다.
          </p>
        </div>
        <CsvUploadSection />
      </main>
    </div>
  )
}
