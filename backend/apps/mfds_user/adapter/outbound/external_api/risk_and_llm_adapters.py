import os
import urllib.request
import urllib.parse
import json
import logging
from datetime import date, datetime
import asyncio
from typing import List, Dict

from mfds_user.app.ports.output.crawler_ports import FoodRiskPort
from mfds_user.app.ports.output.report_llm_port import ReportLLMPort
from mfds_user.domain.value_objects.report_section_vo import ReportSection, SectionType, ReportItem
from mfds_user.domain.value_objects.industry_filter_vo import IndustryFilter

# Import keymaker from matrix
try:
    from matrix.grid_keymaker_secret_manager import get_keymaker
    keymaker = get_keymaker()
except ModuleNotFoundError:
    keymaker = None

logger = logging.getLogger(__name__)

class FoodRiskAdapter(FoodRiskPort):
    def __init__(self) -> None:
        self.api_key = os.getenv("WEATHER_API_KEY")

    async def fetch(self, keywords: List[str]) -> Dict:
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._fetch_sync)

    def _fetch_sync(self) -> Dict:
        if not self.api_key:
            logger.warning("WEATHER_API_KEY is not set - returning default risk")
            return {"level": "medium", "reason": "계절별 식중독 주의 요망", "weather": "날씨 정보 없음"}

        try:
            # Query OpenWeatherMap for Seoul
            query = urllib.parse.urlencode({
                "q": "Seoul,KR",
                "appid": self.api_key,
                "units": "metric",
                "lang": "kr"
            })
            url = f"https://api.openweathermap.org/data/2.5/weather?{query}"
            
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as response:
                payload = json.loads(response.read().decode("utf-8"))
                
            main = payload.get("main") or {}
            temp = main.get("temp", 20.0)
            weather_desc = (payload.get("weather") or [{}])[0].get("description", "맑음")
            
            # Map temp to risk level
            if temp >= 25.0:
                level = "high"
                reason = f"기온 상승({temp}°C)으로 세균 증식 위험 높음. 부패하기 쉬운 식품 냉장 보관 철저."
            elif temp >= 15.0:
                level = "medium"
                reason = f"적정 기온({temp}°C). 보관 온도 주의 및 식재료 신선도 유지."
            else:
                level = "low"
                reason = f"낮은 기온({temp}°C)으로 위험성 낮음. 일상적 위생 관리 준수."
                
            return {
                "level": level,
                "reason": reason,
                "weather": f"서울 {temp}°C, {weather_desc}"
            }
        except Exception as e:
            logger.error(f"Error fetching weather/risk: {e}")
            return {"level": "medium", "reason": "식중독 예방을 위한 위생 수칙 준수 요망", "weather": "날씨 정보 호출 실패"}

class ReportLLMAdapter(ReportLLMPort):
    REPORT_PROMPT_TEMPLATE = """
아래 수집 데이터를 섹션별 HTML 형식으로 변환하세요.
요약·해석·권고 없이 지정된 필드만 추출·정제합니다.

[섹션별 출력 규칙]

NEWS / MFDS / STATS:
- 제목 (원문 그대로) + 하이퍼링크
- 1~2줄 핵심 내용 (수치·날짜 있으면 그대로 포함)
- 출처명 + 날짜

RECALL:
- 제품명 / 식품유형 / 위반사항 / 조치내용 / 유통기한 / 제조지역
- 수치·날짜 원문 그대로 유지
- 출처 하이퍼링크

LAW:
- 법령명 + 하이퍼링크 (조문 직링크 우선)
- 변경내용: 변경전 → 변경후 (수치 있으면 그대로)
- 시행일 / 대상품목

RESEARCH:
- 한국어 번역 제목 (영문 원제 병기)
- 초록 키워드 1~2줄
- 출처(PubMed / ScienceON) + 하이퍼링크

RISK:
- 위험등급 / 한줄 사유 / 날씨 수치

[빈 섹션 처리]
- 수집 데이터가 없는 섹션:
  <p class="empty">당일 특이사항 없음</p>
- 수집은 됐으나 선택 업종({industry_names})과 무관한 경우:
  <p class="empty">해당 업종 관련 특이사항 없음</p>

[공통 규칙]
- 해석·평가·권고 문장 금지 ("주의 필요", "검토 바람" 등 추가 금지)
- URL은 반드시 원본 그대로 유지
- 출력은 아래 HTML 구조만, 다른 텍스트 없이

<article class="daily-report">
  <section class="report-section" data-type="NEWS">
    <h3 class="section-label" data-type="NEWS">[업계뉴스]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{원본URL}}">{{제목}}</a>
        <p class="item-desc">{{1~2줄 내용}}</p>
        <span class="item-source">{{출처}} · {{날짜}}</span>
      </li>
    </ul>
  </section>

  <section class="report-section" data-type="RECALL">
    <h3 class="section-label" data-type="RECALL">[회수·행정처분]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{원본URL}}">{{제품명}} → {{조치내용}}</a>
        <p class="item-desc">{{식품유형}} | {{위반사항}} | 유통기한 {{날짜}} | {{제조지역}}</p>
        <span class="item-source">{{출처}}</span>
      </li>
    </ul>
  </section>

  <section class="report-section" data-type="LAW">
    <h3 class="section-label" data-type="LAW">[법규 변동]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{조문URL}}">{{법령명}}</a>
        <p class="item-desc">{{변경전}} → {{변경후}} | {{시행일}} | 대상: {{품목}}</p>
        <span class="item-source">{{출처}}</span>
      </li>
    </ul>
  </section>

  <section class="report-section" data-type="MFDS">
    <h3 class="section-label" data-type="MFDS">[식약처 보도자료]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{원본URL}}">{{제목}}</a>
        <p class="item-desc">{{1~2줄 내용}}</p>
        <span class="item-source">식약처 · {{날짜}}</span>
      </li>
    </ul>
  </section>

  <section class="report-section" data-type="RISK">
    <h3 class="section-label" data-type="RISK">[식중독 위험 현황]</h3>
    <div class="risk-block" data-level="{{high|medium|low}}">
      <span class="risk-level">{{위험등급}}</span>
      <span class="risk-desc">{{사유}} | {{날씨 수치}}</span>
    </div>
  </section>

  <section class="report-section" data-type="RESEARCH">
    <h3 class="section-label" data-type="RESEARCH">[최신 연구 동향]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{원본URL}}">{{한국어 번역 제목}}</a>
        <p class="item-desc research-en">{{영문 원제}}</p>
        <p class="item-desc">{{초록 키워드 1~2줄}}</p>
        <span class="item-source">{{PubMed|ScienceON}}</span>
      </li>
    </ul>
  </section>

  <section class="report-section" data-type="STATS">
    <h3 class="section-label" data-type="STATS">[식품산업 통계·동향]</h3>
    <ul class="item-list">
      <li class="item-row">
        <a class="item-link" href="{{원본URL}}">{{제목}}</a>
        <p class="item-desc">{{1~2줄 내용}}</p>
        <span class="item-source">FIS 뉴스레터</span>
      </li>
    </ul>
  </section>
</article>

[수집 데이터]
대상 업종: {industry_names}
수집일: {report_date}

## 업계 뉴스
{news_items}

## 회수·행정처분
{recall_items}

## 법규 변동
{law_items}

## 식약처 보도자료
{mfds_items}

## 식중독 위험 현황
{risk_info}

## 최신 연구 동향
{research_items}
-- PubMed(해외) + ScienceON(국내) 최근 30일 논문
-- 영문 제목은 한국어로 번역하여 원문 병기

## 식품산업 통계·동향
{stats_items}
-- FIS 뉴스레터 (월간, 최신 1~3건)
"""

    def _serialize_items(self, items: List[ReportItem]) -> str:
        if not items:
            return "수집 데이터 없음"
        lines = []
        for item in items:
            lines.append(f"- 제목: {item.title}\n  URL: {item.url}\n  출처: {item.source}\n  날짜: {item.published_at.isoformat()}")
        return "\n".join(lines)

    async def generate_summary(
        self,
        sections: List[ReportSection],
        industry_filter: IndustryFilter,
        report_date: date,
    ) -> str:
        if not keymaker or not keymaker.is_gemini_ready():
            logger.warning("Gemini API is not ready - returning mockup report HTML")
            return f"<article class='daily-report'><p>Gemini API 미연결 상태입니다. (수집일: {report_date})</p></article>"

        # Map sections to their formatted values
        sec_map = {s.type: s.items for s in sections}
        
        # Format names for the prompt
        industry_names = ", ".join(industry_filter.media_codes + industry_filter.foodtype_mid_codes)
        if not industry_names:
            industry_names = "전체 업종"

        news_items = self._serialize_items(sec_map.get(SectionType.NEWS, []))
        recall_items = self._serialize_items(sec_map.get(SectionType.RECALL, []))
        law_items = self._serialize_items(sec_map.get(SectionType.LAW, []))
        mfds_items = self._serialize_items(sec_map.get(SectionType.MFDS, []))
        
        # Risk item serialization
        risk_list = sec_map.get(SectionType.RISK, [])
        if risk_list:
            risk_info = f"등급: {risk_list[0].title}, 정보: {risk_list[0].source}"
        else:
            risk_info = "수집 데이터 없음"

        research_items = self._serialize_items(sec_map.get(SectionType.RESEARCH, []))
        stats_items = self._serialize_items(sec_map.get(SectionType.STATS, []))

        prompt = self.REPORT_PROMPT_TEMPLATE.format(
            industry_names=industry_names,
            report_date=report_date.isoformat(),
            news_items=news_items,
            recall_items=recall_items,
            law_items=law_items,
            mfds_items=mfds_items,
            risk_info=risk_info,
            research_items=research_items,
            stats_items=stats_items
        )

        try:
            loop = asyncio.get_running_loop()
            # Call Gemini in thread pool (or standard async if available)
            response = await loop.run_in_executor(None, keymaker.generate_content, prompt)
            
            # Extract plain text response
            text = ""
            if hasattr(response, "text"):
                text = (response.text or "").strip()
            elif isinstance(response, str):
                text = response.strip()
                
            # Strip markdown code blocks if the model wrapped it in ```html ... ```
            if text.startswith("```"):
                # strip ```html or ``` and trailing ```
                lines = text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = "\n".join(lines).strip()
                
            if not text:
                raise ValueError("Model returned an empty briefing summary.")
                
            return text
        except Exception as e:
            logger.error(f"Error generating daily briefing report via Gemini: {e}")
            return f"<article class='daily-report'><p>일일 브리핑 요약 생성 도중 오류가 발생했습니다: {e}</p></article>"
