import { ClipboardList, MessageSquare, FileCheck } from "lucide-react"

const steps = [
  {
    step: "01",
    icon: ClipboardList,
    title: "원료 등록",
    description: "우리 회사에서 사용하는 원료 목록을 등록합니다",
  },
  {
    step: "02",
    icon: MessageSquare,
    title: "AI 질의",
    description: "구어체로 위해식품 현황을 물어봅니다",
  },
  {
    step: "03",
    icon: FileCheck,
    title: "리포트 확인",
    description: "원료 매칭 결과와 HACCP 조치 권고사항을 확인합니다",
  },
]

export function HowItWorksSection() {
  return (
    <section id="how-it-works" className="scroll-mt-24 border-y border-border bg-secondary/30 py-20 md:py-28">
      <div className="container mx-auto px-4">
        <div className="mb-16 text-center">
          <h2 className="mb-4 text-balance text-3xl font-bold text-foreground md:text-4xl">
            3단계로 간단하게
          </h2>
          <p className="mx-auto max-w-2xl text-pretty text-muted-foreground">
            복잡한 설정 없이 바로 시작할 수 있습니다
          </p>
        </div>

        <div className="relative mx-auto max-w-4xl">
          {/* Connection Line (Desktop) */}
          <div className="absolute left-0 right-0 top-16 hidden h-0.5 bg-gradient-to-r from-transparent via-primary/30 to-transparent md:block" />

          <div className="grid gap-8 md:grid-cols-3">
            {steps.map((item, index) => (
              <div key={index} className="relative flex flex-col items-center text-center">
                {/* Step Number & Icon */}
                <div className="relative mb-6">
                  <div className="flex h-32 w-32 items-center justify-center rounded-full border border-border bg-card shadow-lg">
                    <div className="flex h-20 w-20 items-center justify-center rounded-full bg-primary/10">
                      <item.icon className="h-10 w-10 text-primary" />
                    </div>
                  </div>
                  <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-sm font-bold text-primary-foreground">
                    {item.step}
                  </div>
                </div>

                <h3 className="mb-2 text-xl font-semibold text-foreground">{item.title}</h3>
                <p className="text-muted-foreground">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}
