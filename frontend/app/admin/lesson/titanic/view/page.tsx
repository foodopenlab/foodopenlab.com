import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { WalterIntroSection } from "@/components/titanic/walter-intro-section"

export default function TitanicViewPage() {
  return (
    <div className="container mx-auto max-w-6xl px-4 py-10">
      <Card className="border-border/50 bg-card/80 shadow-xl backdrop-blur-md">
        <CardHeader>
          <CardTitle>2. 탑승자 목록</CardTitle>
          <CardDescription>월터 로스터가 타이타닉 승무원으로 자신을 소개합니다.</CardDescription>
        </CardHeader>
        <CardContent>
          <WalterIntroSection />
        </CardContent>
      </Card>
    </div>
  )
}
