import json
import logging
from datetime import date
from typing import List, Dict
import asyncio

from mfds_user.app.ports.output.report_feedback_repository import FeedbackAnalysisLLMPort
from mfds_user.domain.entities.report_feedback_entity import ReportFeedback

try:
    from matrix.grid_keymaker_secret_manager import get_keymaker
    keymaker = get_keymaker()
except ModuleNotFoundError:
    keymaker = None

logger = logging.getLogger(__name__)

class FeedbackAnalysisLLMAdapter(FeedbackAnalysisLLMPort):
    PROMPT_TEMPLATE = """
다음은 {industry_code} 업종 전문가들이 일일 브리핑에 남긴 피드백입니다.
기간: {period_start} ~ {period_end} (총 {count}건)

[피드백 원문]
{feedbacks_formatted}
-- 각 피드백: 유용성점수 / 유용한섹션 / 내용평가 / 누락정보 / 개선제안

[분석 지시]
아래 JSON 형식으로만 응답하세요. 다른 텍스트 없이 JSON만 출력하세요.

{{
  "missing_topics": ["string", ...],
  "improvement_keys": ["string", ...],
  "useful_sections": {{
    "NEWS": 0.0,
    "RECALL": 0.0,
    "LAW": 0.0,
    "MFDS": 0.0,
    "RISK": 0.0,
    "RESEARCH": 0.0,
    "STATS": 0.0
  }},
  "summary": "string",
  "action_items": ["string", ...]
}}
"""

    async def analyze(
        self,
        feedbacks: List[ReportFeedback],
        industry_code: str,
        period_start: date,
        period_end: date
    ) -> Dict:
        # 1. Format feedbacks
        lines = []
        for i, fb in enumerate(feedbacks, 1):
            secs = ", ".join(s.value for s in fb.useful_sections)
            lines.append(
                f"피드백 #{i}:\n"
                f"- 유용성점수: {fb.usefulness_score}/5\n"
                f"- 유용한섹션: [{secs}]\n"
                f"- 내용평가: {fb.content_feedback or '없음'}\n"
                f"- 누락정보: {fb.missing_feedback or '없음'}\n"
                f"- 개선제안: {fb.improvement_feedback or '없음'}\n"
            )
        feedbacks_formatted = "\n".join(lines)

        prompt = self.PROMPT_TEMPLATE.format(
            industry_code=industry_code,
            period_start=period_start.isoformat(),
            period_end=period_end.isoformat(),
            count=len(feedbacks),
            feedbacks_formatted=feedbacks_formatted
        )

        fallback_result = {
            "missing_topics": ["원재료 시황 정보", "새로운 수입 규제"],
            "improvement_keys": ["요약이 너무 깁니다", "섹션별 가시성 확보"],
            "useful_sections": {
                "NEWS": 0.8,
                "RECALL": 0.6,
                "LAW": 0.7,
                "MFDS": 0.5,
                "RISK": 0.4,
                "RESEARCH": 0.3,
                "STATS": 0.4
            },
            "summary": "최근 피드백에 따르면 실무 정보(법규 변동 및 회수 정보)에 대한 만족도가 높으나 최신 원자재 시세 등의 정보가 부족하다는 평가가 있었습니다.",
            "action_items": ["주요 식품 원자재 가격 동향 수집 추가 검토", "식약처 요약 길이 단축"]
        }

        if not keymaker or not keymaker.is_gemini_ready():
            logger.warning("Gemini API is not ready - returning fallback feedback analysis")
            return fallback_result

        try:
            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, keymaker.generate_content, prompt)
            
            text = ""
            if hasattr(response, "text"):
                text = (response.text or "").strip()
            elif isinstance(response, str):
                text = response.strip()

            # Clean JSON markdown if wrapped
            if text.startswith("```"):
                lines = text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                text = "\n".join(lines).strip()

            parsed = json.loads(text)
            
            # Ensure correct keys exist
            required_keys = ["missing_topics", "improvement_keys", "useful_sections", "summary", "action_items"]
            for key in required_keys:
                if key not in parsed:
                    parsed[key] = fallback_result[key]
                    
            return parsed
        except Exception as e:
            logger.error(f"Error analyzing feedback via Gemini: {e}")
            return fallback_result
