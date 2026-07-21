from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from typing import List, Annotated
from uuid import UUID
import re
from datetime import date

from mfds_user.dependencies.auth_helper import verify_token, UserTokenPayload
from matrix.grid_admin_guard_manager import verify_admin_jwt

from mfds_user.app.ports.input.daily_report_use_case import DailyReportUseCase
from mfds_user.dependencies.daily_report import get_daily_report_use_case
from mfds_user.app.ports.input.report_scheduler_use_case import ReportSchedulerUseCase
from mfds_user.dependencies.daily_report import get_report_scheduler_use_case
from mfds_user.adapter.inbound.api.schemas.daily_report_schema import (
    DailyReportSchema,
    ReportSectionSchema,
    ReportItemSchema,
    SchedulerResultSchema
)

router = APIRouter(prefix="", tags=["daily-reports"])

def _normalize_report_item_url(raw: str) -> str:
    """저장된 과거 리포트의 localhost 링크/깨진 링크를 UI 친화적으로 보정."""
    url = (raw or "").strip()
    if not url:
        return ""
    # 과거 저장분(로컬 고정 링크) 보정
    if url.startswith("http://127.0.0.1:8000/recalls/") or url.startswith("http://localhost:8000/recalls/"):
        recall_id = url.rsplit("/", 1)[-1]
        return f"/recalls/{recall_id}"
    # 리콜 상세는 프론트 라우트가 SSOT
    if "/recalls/" in url and (url.startswith("http://127.0.0.1:8000") or url.startswith("http://localhost:8000")):
        recall_id = url.rsplit("/", 1)[-1]
        return f"/recalls/{recall_id}"
    # FIS는 list url이 404가 잦아 랜딩으로 보정
    if "atfis.or.kr" in url and "newsletter/list.do" in url:
        return "https://www.atfis.or.kr"
    return url

def _to_schema(report) -> DailyReportSchema:
    return DailyReportSchema(
        id=str(report.id),
        expert_user_id=str(report.expert_user_id),
        report_date=report.report_date,
        generated_at=report.generated_at,
        expires_at=report.expires_at,
        is_saved=report.is_saved,
        summary=report.summary,
        summary_preview=report.summary_preview,
        sections=[
            ReportSectionSchema(
                type=s.type.value,
                items=[
                    ReportItemSchema(
                        title=item.title,
                        url=_normalize_report_item_url(item.url),
                        source=item.source,
                        published_at=item.published_at
                    )
                    for item in s.items
                ],
                is_empty=s.is_empty
            )
            for s in report.sections
        ]
    )

@router.get("/mypage/reports", response_model=List[DailyReportSchema])
async def get_my_reports(
    token: UserTokenPayload = Depends(verify_token),
    use_case: DailyReportUseCase = Depends(get_daily_report_use_case)
) -> List[DailyReportSchema]:
    user_id = UUID(token.sub)
    reports = await use_case.get_my_reports(user_id)
    return [_to_schema(r) for r in reports]

@router.get("/mypage/reports/{id}", response_model=DailyReportSchema)
async def get_report_detail(
    id: str,
    token: UserTokenPayload = Depends(verify_token),
    use_case: DailyReportUseCase = Depends(get_daily_report_use_case)
) -> DailyReportSchema:
    user_id = UUID(token.sub)
    try:
        report = await use_case.get_report_detail(user_id, UUID(id))
        return _to_schema(report)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/mypage/reports/{id}/save", response_model=DailyReportSchema)
async def save_report(
    id: str,
    token: UserTokenPayload = Depends(verify_token),
    use_case: DailyReportUseCase = Depends(get_daily_report_use_case)
) -> DailyReportSchema:
    user_id = UUID(token.sub)
    try:
        report = await use_case.save_report(user_id, UUID(id))
        return _to_schema(report)
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/mypage/reports/{id}/download")
async def download_report(
    id: str,
    token: UserTokenPayload = Depends(verify_token),
    use_case: DailyReportUseCase = Depends(get_daily_report_use_case)
):
    user_id = UUID(token.sub)
    try:
        report = await use_case.get_report_detail(user_id, UUID(id))
        
        # Convert HTML summary to clean plain text for download
        plain_text = re.sub(r'<[^>]+>', '', report.summary)
        plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text)
        
        filename = f"daily_report_{report.report_date.isoformat()}.txt"
        return Response(
            content=plain_text,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    except (ValueError, PermissionError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.post("/admin/reports/generate", response_model=SchedulerResultSchema)
async def trigger_scheduler_batch(
    _admin: Annotated[str, Depends(verify_admin_jwt)],
    use_case: ReportSchedulerUseCase = Depends(get_report_scheduler_use_case)
) -> SchedulerResultSchema:
    try:
        res = await use_case.generate_all()
        return SchedulerResultSchema(
            success=res["success"],
            fail=res["fail"],
            skipped=res["skipped"],
            total=res["total"]
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/admin/reports/regenerate", response_model=DailyReportSchema)
async def regenerate_report_for_user_and_date(
    _admin: Annotated[str, Depends(verify_admin_jwt)],
    expert_user_id: str = "",
    report_date: str = "",
    use_case: DailyReportUseCase = Depends(get_daily_report_use_case),
) -> DailyReportSchema:
    try:
        if not expert_user_id or not report_date:
            raise ValueError("expert_user_id와 report_date(YYYY-MM-DD)는 필수입니다.")
        d = date.fromisoformat(report_date)
        report = await use_case.generate_for_date(UUID(expert_user_id), d, force_refresh=True)
        return _to_schema(report)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
