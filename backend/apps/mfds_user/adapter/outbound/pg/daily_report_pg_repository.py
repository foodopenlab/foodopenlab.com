from typing import Any, List, Optional, cast
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import select, delete, and_
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from mfds_user.app.ports.output.daily_report_repository import DailyReportRepository
from mfds_user.domain.entities.daily_report_entity import DailyReport
from mfds_user.domain.value_objects.report_section_vo import ReportSection, SectionType, ReportItem
from mfds_user.adapter.outbound.orm.daily_report_orm import DailyReportORM

class DailyReportPgRepository(DailyReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _to_entity(self, orm: DailyReportORM) -> DailyReport:
        def make_section(type_: SectionType, raw_data) -> ReportSection:
            items = []
            if isinstance(raw_data, list):
                for item in raw_data:
                    # published_at in JSON is serialized as string
                    pub_at = date.fromisoformat(item["published_at"]) if isinstance(item.get("published_at"), str) else date.today()
                    items.append(ReportItem(
                        title=item.get("title", ""),
                        url=item.get("url", ""),
                        source=item.get("source", ""),
                        published_at=pub_at
                    ))
            elif isinstance(raw_data, dict) and raw_data.get("title"):
                # Handle risk dict
                pub_at = date.fromisoformat(raw_data["published_at"]) if isinstance(raw_data.get("published_at"), str) else date.today()
                items.append(ReportItem(
                    title=raw_data.get("title", ""),
                    url=raw_data.get("url", ""),
                    source=raw_data.get("source", ""),
                    published_at=pub_at
                ))
            return ReportSection(
                type=type_,
                items=items,
                is_empty=len(items) == 0
            )

        sections = [
            make_section(SectionType.NEWS,     orm.raw_news),
            make_section(SectionType.RECALL,   orm.raw_recalls),
            make_section(SectionType.LAW,      orm.raw_laws),
            make_section(SectionType.MFDS,     orm.raw_mfds),
            make_section(SectionType.RISK,     orm.raw_risk),
            make_section(SectionType.RESEARCH, orm.raw_research),
            make_section(SectionType.STATS,    orm.raw_stats),
        ]

        return DailyReport(
            id=orm.id,
            expert_user_id=orm.expert_user_id,
            report_date=orm.report_date,
            generated_at=orm.generated_at,
            expires_at=orm.expires_at,
            is_saved=orm.is_saved,
            summary=orm.summary,
            summary_preview=orm.summary_preview,
            sections=sections
        )

    def _serialize_sections(self, sections: List[ReportSection]) -> dict:
        serialized = {}
        for s in sections:
            list_data = [
                {
                    "title": item.title,
                    "url": item.url,
                    "source": item.source,
                    "published_at": item.published_at.isoformat()
                }
                for item in s.items
            ]
            if s.type == SectionType.NEWS:
                serialized["raw_news"] = list_data
            elif s.type == SectionType.RECALL:
                serialized["raw_recalls"] = list_data
            elif s.type == SectionType.LAW:
                serialized["raw_laws"] = list_data
            elif s.type == SectionType.MFDS:
                serialized["raw_mfds"] = list_data
            elif s.type == SectionType.RISK:
                serialized["raw_risk"] = list_data[0] if list_data else {}
            elif s.type == SectionType.RESEARCH:
                serialized["raw_research"] = list_data
            elif s.type == SectionType.STATS:
                serialized["raw_stats"] = list_data
        return serialized

    async def find_by_user(self, expert_user_id: UUID) -> List[DailyReport]:
        stmt = select(DailyReportORM).where(
            DailyReportORM.expert_user_id == expert_user_id
        ).order_by(DailyReportORM.report_date.desc())
        res = await self.session.execute(stmt)
        rows = res.scalars().all()
        return [self._to_entity(r) for r in rows]

    async def find_by_user_and_date(self, expert_user_id: UUID, report_date: date) -> Optional[DailyReport]:
        stmt = select(DailyReportORM).where(
            and_(
                DailyReportORM.expert_user_id == expert_user_id,
                DailyReportORM.report_date == report_date
            )
        )
        res = await self.session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

    async def find(self, report_id: UUID) -> Optional[DailyReport]:
        stmt = select(DailyReportORM).where(DailyReportORM.id == report_id)
        res = await self.session.execute(stmt)
        orm = res.scalar_one_or_none()
        return self._to_entity(orm) if orm else None

    async def save(self, report: DailyReport) -> DailyReport:
        serialized = self._serialize_sections(report.sections)
        db_report = DailyReportORM(
            id=report.id,
            expert_user_id=report.expert_user_id,
            report_date=report.report_date,
            generated_at=report.generated_at,
            expires_at=report.expires_at,
            is_saved=report.is_saved,
            summary=report.summary,
            summary_preview=report.summary_preview,
            **serialized
        )
        self.session.add(db_report)
        await self.session.commit()
        return report

    async def update(self, report: DailyReport) -> DailyReport:
        stmt = select(DailyReportORM).where(DailyReportORM.id == report.id)
        res = await self.session.execute(stmt)
        db_report = res.scalar_one()
        
        db_report.is_saved = report.is_saved
        serialized = self._serialize_sections(report.sections)
        for k, v in serialized.items():
            setattr(db_report, k, v)
            
        await self.session.commit()
        return report

    async def delete_expired_unsaved(self, expert_user_id: UUID) -> None:
        stmt = delete(DailyReportORM).where(
            and_(
                DailyReportORM.expert_user_id == expert_user_id,
                DailyReportORM.is_saved == False,
                DailyReportORM.expires_at < datetime.utcnow()
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def delete_by_user_and_date(self, expert_user_id: UUID, report_date: date) -> bool:
        stmt = delete(DailyReportORM).where(
            and_(
                DailyReportORM.expert_user_id == expert_user_id,
                DailyReportORM.report_date == report_date,
            )
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        deleted = cast(CursorResult[Any], result).rowcount or 0
        return deleted > 0
