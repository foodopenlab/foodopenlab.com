import type { Metadata } from "next"
import { InfoPageShell } from "@/components/landing/info-page-shell"

export const metadata: Metadata = {
  title: "개인정보처리방침 | HACCP Monitor AI",
  description: "HACCP Monitor AI 개인정보처리방침",
}

export default function PrivacyPage() {
  return (
    <InfoPageShell
      title="개인정보처리방침"
      description="HACCP Monitor AI가 수집·이용하는 개인정보에 관한 안내입니다."
    >
      <p className="text-sm text-muted-foreground">시행일: 2025년 1월 1일</p>

      <h2>1. 수집하는 개인정보 항목</h2>
      <ul>
        <li>회원가입: 이메일, 비밀번호(암호화 저장), 이름 또는 표시명</li>
        <li>서비스 이용: 접속 로그, API 이용 기록, 채팅·검색 이력(서비스 개선 목적)</li>
        <li>비회원: 별도 가입 없이 쿠키·세션 식별자로 일부 이용 로그가 기록될 수 있습니다.</li>
      </ul>

      <h2>2. 개인정보의 이용 목적</h2>
      <ul>
        <li>회원 식별, 로그인 및 마이페이지 제공</li>
        <li>식품안전 관련 조회·분석 서비스 제공</li>
        <li>서비스 품질 개선, 오류 대응, 보안</li>
      </ul>

      <h2>3. 보관 및 파기</h2>
      <p>
        회원 탈퇴 시 관련 법령에 따른 보존 의무를 제외하고 지체 없이 파기합니다. 채팅·검색 로그는 운영
        정책에 따라 일정 기간 보관 후 삭제될 수 있습니다.
      </p>

      <h2>4. 제3자 제공</h2>
      <p>
        원칙적으로 이용자의 개인정보를 외부에 제공하지 않습니다. 다만 법령에 따른 요청이 있는 경우
        예외적으로 제공될 수 있습니다.
      </p>

      <h2>5. 이용자 권리</h2>
      <p>
        마이페이지 또는 고객 문의를 통해 개인정보 열람·정정·삭제·처리 정지·회원 탈퇴를 요청할 수
        있습니다.
      </p>

      <h2>6. 문의</h2>
      <p>
        개인정보 관련 문의는 <a href="/contact">문의하기</a> 페이지를 이용해 주세요.
      </p>

      <p className="text-xs text-muted-foreground">
        본 방침은 서비스 변경에 따라 개정될 수 있으며, 중요한 변경 시 사전 공지합니다.
      </p>
    </InfoPageShell>
  )
}
