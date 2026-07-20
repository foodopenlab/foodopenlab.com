import type { Metadata } from "next"
import { InfoPageShell } from "@/components/landing/info-page-shell"

export const metadata: Metadata = {
  title: "이용약관 | HACCP Monitor AI",
  description: "HACCP Monitor AI 이용약관",
}

export default function TermsPage() {
  return (
    <InfoPageShell
      title="이용약관"
      description="HACCP Monitor AI 서비스 이용에 관한 기본 약관입니다."
    >
      <p className="text-sm text-muted-foreground">시행일: 2025년 1월 1일</p>

      <h2>제1조 (목적)</h2>
      <p>
        본 약관은 HACCP Monitor AI(이하 &quot;서비스&quot;)의 이용 조건 및 절차, 이용자와 운영자 간
        권리·의무를 규정합니다.
      </p>

      <h2>제2조 (서비스 내용)</h2>
      <p>
        서비스는 공공데이터 및 AI 분석을 활용한 식품안전 정보 조회·모니터링 기능을 제공합니다. 제공
        정보는 공공 API·캐시 데이터 기준이며, 법적 효력이 있는 공식 확인 수단이 아닙니다.
      </p>

      <h2>제3조 (회원 가입 및 등급)</h2>
      <ul>
        <li>누구나 이메일 또는 소셜 계정(구글·카카오·네이버)으로 회원가입할 수 있으며, 가입 시 일반회원으로 시작합니다.</li>
        <li>전문가회원 권한은 운영자(관리자)의 심사·승인을 거쳐 부여되며, 이후 전문가 전용 기능을 이용할 수 있습니다.</li>
        <li>회원은 정확한 정보를 제공해야 하며, 계정 관리 책임은 회원에게 있습니다.</li>
      </ul>

      <h2>제4조 (이용자의 의무)</h2>
      <ul>
        <li>타인의 정보를 도용하거나 서비스를 부정 이용해서는 안 됩니다.</li>
        <li>서비스를 통해 얻은 정보는 내부 업무 목적으로 활용하고, 무단 재배포를 금합니다.</li>
        <li>AI 분석 결과는 참고 자료이며, 최종 판단은 이용자의 책임입니다.</li>
      </ul>

      <h2>제5조 (서비스 변경·중단)</h2>
      <p>
        운영상·기술상 필요에 따라 서비스의 전부 또는 일부를 변경·중단할 수 있으며, 가능한 경우 사전에
        공지합니다.
      </p>

      <h2>제6조 (면책)</h2>
      <p>
        공공 API 장애, 데이터 지연, AI 응답 오류 등으로 인한 손해에 대해 운영자는 고의 또는 중대한
        과실이 없는 한 책임을 지지 않습니다.
      </p>

      <h2>제7조 (문의)</h2>
      <p>
        약관 관련 문의는 <a href="/contact">문의하기</a>를 이용해 주세요.
      </p>
    </InfoPageShell>
  )
}
