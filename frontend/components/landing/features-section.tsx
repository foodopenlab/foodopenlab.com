import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Search, Bot, AlertTriangle } from "lucide-react"

const features = [
  {
    icon: Search,
    title: "복합 조건 검색",
    description: "원료명, 식품유형, 회수사유, 지역, 기간을 자유롭게 조합하여 검색",
  },
  {
    icon: Bot,
    title: "구어체로 질의",
    description: "'이번 달 미생물 회수 알려줘'처럼 구어체로 물어보면 AI가 파라미터를 자동 추출",
  },
  {
    icon: AlertTriangle,
    title: "원료 위험도 자동 평가",
    description: "우리 회사 원료 목록과 회수 원료를 대조하여 HIGH/MEDIUM/LOW로 위험도를 즉시 평가",
  },
]

export function FeaturesSection() {
  return (
    <section id="features" className="scroll-mt-24 py-20 md:py-28">
      <div className="container mx-auto px-4">
        <div className="mb-12 text-center">
          <h2 className="mb-4 text-balance text-3xl font-bold text-foreground md:text-4xl">
            HACCP 담당자를 위한 스마트 모니터링
          </h2>
          <p className="mx-auto max-w-2xl text-pretty text-muted-foreground">
            복잡한 위해식품 정보를 한눈에 파악하고, AI의 도움으로 빠르게 대응하세요
          </p>
        </div>

        <div className="grid gap-6 md:grid-cols-3">
          {features.map((feature, index) => (
            <Card 
              key={index} 
              className="group border-border bg-card transition-all duration-300 hover:border-primary/50 hover:shadow-lg hover:shadow-primary/5"
            >
              <CardHeader>
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10 text-primary transition-colors group-hover:bg-primary group-hover:text-primary-foreground">
                  <feature.icon className="h-6 w-6" />
                </div>
                <CardTitle className="text-xl text-foreground">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base text-muted-foreground">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
