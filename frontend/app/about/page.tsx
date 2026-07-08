import type { Metadata } from "next"
import { InfoPageShell } from "@/components/landing/info-page-shell"

export const metadata: Metadata = {
  title: "서비스 소개 | HACCP Monitor AI",
  description: "HACCP Monitor AI 서비스 소개",
}

export default function AboutPage() {
  return (
    <InfoPageShell
      title="서비스 소개"
      description="식품안전 공공데이터와 AI를 활용한 위해식품·행정처분 모니터링 서비스입니다."
    >
      <h2>HACCP Monitor AI란?</h2>
      <p>
        HACCP Monitor AI는 식품안전나라 등 공공 API와 연동하여 위해식품 회수, 행정처분, HACCP 인증 정보를
        한곳에서 조회·분석할 수 있도록 돕는 모니터링 도구입니다.
      </p>

      <h2>주요 기능</h2>
      <ul>
        <li>위해식품 회수·판매중지 정보 조회</li>
        <li>식품 영업소 행정처분 이력 검색</li>
        <li>원료·법규 관련 AI 분석 채팅</li>
        <li>전문가 회원용 일일 리포트 및 업종 설정</li>
      </ul>

      <h2>이용 대상</h2>
      <p>
        식품 제조·유통 업체의 품질·안전 담당자, HACCP 실무자, 식품 안전 컨설턴트 등을 주요 이용 대상으로
        합니다. 비회원도 대부분의 공공데이터 조회 기능을 이용할 수 있습니다.
      </p>

      <p className="text-xs text-muted-foreground">
        본 페이지의 서비스 설명은 운영 정책에 따라 업데이트될 수 있습니다.
      </p>
    </InfoPageShell>
  )
}
