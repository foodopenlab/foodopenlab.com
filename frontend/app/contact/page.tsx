import type { Metadata } from "next"
import Link from "next/link"
import { InfoPageShell } from "@/components/landing/info-page-shell"
import { Button } from "@/components/ui/button"

export const metadata: Metadata = {
  title: "문의하기 | HACCP Monitor AI",
  description: "HACCP Monitor AI 문의 안내",
}

export default function ContactPage() {
  return (
    <InfoPageShell
      title="문의하기"
      description="서비스 이용, 회원가입, 개인정보 관련 문의를 안내합니다."
    >
      <h2>문의 방법</h2>
      <p>
        아래 채널로 문의해 주시면 영업일 기준 순차적으로 답변드립니다. 긴급한 식품안전 이슈는
        식품의약품안전처·식품안전나라 공식 채널을 이용해 주세요.
      </p>

      <div className="not-prose my-6 rounded-xl border border-border bg-card p-5 space-y-4">
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">이메일</p>
          <p className="mt-1 text-sm font-medium text-foreground">support@foodopenlab.com</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">운영 시간</p>
          <p className="mt-1 text-sm text-muted-foreground">평일 09:00 – 18:00 (공휴일 제외)</p>
        </div>
        <div>
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">답변 안내</p>
          <p className="mt-1 text-sm text-muted-foreground">
            접수 후 1–3영업일 이내 회신을 목표로 합니다.
          </p>
        </div>
      </div>

      <h2>자주 문의하는 내용</h2>
      <ul>
        <li>전문가 회원 화이트리스트 등록 요청</li>
        <li>회원가입·로그인 오류</li>
        <li>행정처분·회수 데이터 조회 문제</li>
        <li>개인정보 열람·삭제 요청</li>
      </ul>

      <div className="not-prose mt-8 flex flex-wrap gap-3">
        <Button asChild>
          <a href="mailto:support@foodopenlab.com">이메일 보내기</a>
        </Button>
        <Button variant="outline" asChild>
          <Link href="/">홈으로 돌아가기</Link>
        </Button>
      </div>
    </InfoPageShell>
  )
}
