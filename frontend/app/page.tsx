// 랜딩 히어로 우측 `HeroInsightsColumn` → 행정처분은 Next `/api/sanctions/latest`가 com.auditor `sanction_cache.json`(sync catalog 기준)을 우선 표시합니다.
// 채팅 툴바(빠른 모델·마이크·보내기) 레이아웃: gemini-landing-chat-toolbar-layout.ts
// 버튼 크롬(보내기 초록 등): gemini-landing-chat-toolbar-controls.ts + components/ui/button.tsx
import { GeminiLandingChat } from "@/components/landing/gemini-landing-chat"
import { HeroSection } from "@/components/landing/hero-section"
import { LogosSection } from "@/components/landing/logos-section"
import { Footer } from "@/components/landing/footer"

export default function LandingPage() {
  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <main className="flex-1">
        <HeroSection geminiChat={<GeminiLandingChat compact />} />
        <LogosSection />
      </main>
      <Footer />
    </div>
  )
}
