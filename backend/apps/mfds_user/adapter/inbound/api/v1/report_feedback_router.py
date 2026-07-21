from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from uuid import UUID

from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from matrix.grid_admin_guard_manager import verify_admin_jwt

from mfds_user.app.ports.input.report_feedback_use_case import ReportFeedbackUseCase
from mfds_user.dependencies.report_feedback import get_report_feedback_use_case
from mfds_user.domain.value_objects.report_section_vo import SectionType
from mfds_user.adapter.inbound.api.schemas.report_feedback_schema import (
    FeedbackSubmitRequestSchema,
    FeedbackResponseSchema,
    FeedbackAnalysisTriggerRequestSchema,
    FeedbackAnalysisResponseSchema
)

router = APIRouter(prefix="", tags=["report-feedbacks"])

def _to_schema(fb) -> FeedbackResponseSchema:
    return FeedbackResponseSchema(
        id=str(fb.id),
        report_id=str(fb.report_id),
        expert_user_id=str(fb.expert_user_id),
        created_at=fb.created_at,
        useful_sections=[s.value for s in fb.useful_sections],
        content_feedback=fb.content_feedback,
        missing_feedback=fb.missing_feedback,
        improvement_feedback=fb.improvement_feedback,
        usefulness_score=fb.usefulness_score
    )

@router.post("/mypage/reports/{id}/feedback", response_model=FeedbackResponseSchema, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    id: str,
    req: FeedbackSubmitRequestSchema,
    token: UserTokenPayload = Depends(verify_token),
    use_case: ReportFeedbackUseCase = Depends(get_report_feedback_use_case)
) -> FeedbackResponseSchema:
    user_id = UUID(token.sub)
    try:
        sections = [SectionType(s) for s in req.useful_sections]
        fb = await use_case.submit_feedback(
            expert_user_id=user_id,
            report_id=UUID(id),
            useful_sections=sections,
            content_feedback=req.content_feedback,
            missing_feedback=req.missing_feedback,
            improvement_feedback=req.improvement_feedback,
            usefulness_score=req.usefulness_score
        )
        return _to_schema(fb)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/mypage/reports/{id}/feedback", response_model=FeedbackResponseSchema)
async def get_my_feedback(
    id: str,
    token: UserTokenPayload = Depends(verify_token),
    use_case: ReportFeedbackUseCase = Depends(get_report_feedback_use_case)
) -> FeedbackResponseSchema:
    user_id = UUID(token.sub)
    fb = await use_case.get_feedback(user_id, UUID(id))
    if not fb:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="피드백이 아직 존재하지 않습니다.")
    return _to_schema(fb)

@router.get("/admin/report-feedback/analysis", response_model=List[FeedbackAnalysisResponseSchema])
async def get_feedback_analysis(
    _admin: Annotated[str, Depends(verify_admin_jwt)],
    industry_code: str | None = None,
    use_case: ReportFeedbackUseCase = Depends(get_report_feedback_use_case)
) -> List[FeedbackAnalysisResponseSchema]:
    res = await use_case.get_feedback_analysis(industry_code)
    return [
        FeedbackAnalysisResponseSchema(
            id=str(item.id),
            industry_code=item.industry_code,
            analyzed_at=item.analyzed_at,
            feedback_count=item.feedback_count,
            period_start=item.period_start,
            period_end=item.period_end,
            missing_topics=item.missing_topics,
            improvement_keys=item.improvement_keys,
            useful_sections=item.useful_sections,
            summary=item.summary,
            action_items=item.action_items
        )
        for item in res
    ]

@router.post("/admin/report-feedback/analyze", response_model=FeedbackAnalysisResponseSchema)
async def analyze_feedback(
    req: FeedbackAnalysisTriggerRequestSchema,
    _admin: Annotated[str, Depends(verify_admin_jwt)],
    use_case: ReportFeedbackUseCase = Depends(get_report_feedback_use_case)
) -> FeedbackAnalysisResponseSchema:
    try:
        item = await use_case.analyze_feedback(req.industry_code, req.period_start, req.period_end)
        return FeedbackAnalysisResponseSchema(
            id=str(item.id),
            industry_code=item.industry_code,
            analyzed_at=item.analyzed_at,
            feedback_count=item.feedback_count,
            period_start=item.period_start,
            period_end=item.period_end,
            missing_topics=item.missing_topics,
            improvement_keys=item.improvement_keys,
            useful_sections=item.useful_sections,
            summary=item.summary,
            action_items=item.action_items
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
