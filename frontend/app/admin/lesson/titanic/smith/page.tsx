import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SmithCaptainChat } from "@/components/titanic/smith-captain-chat"

export default function TitanicSmithPage() {
  return (
    <div className="container mx-auto max-w-4xl px-4 py-10">
      <div className="mb-8 space-y-3 text-center">
        <p className="text-xs font-semibold tracking-[0.24em] text-muted-foreground">TITANIC DATASET · STEP 3</p>
        <h1 className="text-4xl font-black tracking-tight text-foreground sm:text-5xl">3. 스미스 선장</h1>
        <p className="mx-auto max-w-2xl text-sm text-muted-foreground sm:text-base">
          타이타닉 선장 에드워드 스미스와 대화하며 사고 당시의 결정과 역사적 맥락을 탐구합니다.
        </p>
      </div>
      <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
        <CardHeader>
          <CardTitle>스미스 선장과 대화</CardTitle>
          <CardDescription>선장의 시각에서 타이타닉 항해와 침몰에 대해 질문해 보세요.</CardDescription>
        </CardHeader>
        <CardContent>
          <SmithCaptainChat />
        </CardContent>
      </Card>
    </div>
  )
}
