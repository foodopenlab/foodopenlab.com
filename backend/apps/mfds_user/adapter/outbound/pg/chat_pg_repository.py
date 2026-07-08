from typing import Optional, Any
from uuid import UUID
from datetime import datetime
from sqlalchemy import select, delete, update, func, and_, desc, or_, case
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from mfds_user.app.ports.output.chat_repository import ChatRepository
from mfds_user.domain.entities.agent_message_entity import AgentMessage
from mfds_user.domain.value_objects.query_pattern_vo import QueryPattern
from mfds_user.adapter.outbound.orm.user_orm import UserORM
from mfds_user.adapter.outbound.orm.agent_session_orm import AgentSessionORM
from mfds_user.adapter.outbound.orm.agent_message_orm import AgentMessageORM
from mfds_user.adapter.outbound.orm.agent_message_sources_orm import AgentMessageSourceORM
from mfds_user.adapter.outbound.orm.satisfaction_feedback_orm import SatisfactionFeedbackORM
from mfds_user.adapter.outbound.orm.expert_feedback_orm import ExpertFeedbackORM

class ChatPgRepository(ChatRepository):
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def find_session(self, session_id: UUID) -> Optional[dict]:
        query = select(AgentSessionORM, UserORM.user_type).join(
            UserORM, AgentSessionORM.actor_id == UserORM.id
        ).where(AgentSessionORM.id == session_id)
        result = await self.session.execute(query)
        row = result.first()
        if row:
            db_sess, user_type = row
            return {
                "id": db_sess.id,
                "actor_type": user_type,
                "actor_id": db_sess.actor_id,
                "started_at": db_sess.started_at,
                "last_active_at": db_sess.last_active_at
            }
        return None

    async def create_session(self, session_id: UUID, actor_type: str, actor_id: UUID) -> dict:
        db_sess = AgentSessionORM(
            id=session_id,
            actor_id=actor_id,
            started_at=datetime.utcnow(),
            last_active_at=datetime.utcnow()
        )
        self.session.add(db_sess)
        await self.session.commit()
        return {
            "id": db_sess.id,
            "actor_type": actor_type,
            "actor_id": db_sess.actor_id,
            "started_at": db_sess.started_at,
            "last_active_at": db_sess.last_active_at
        }

    async def update_session_active(self, session_id: UUID) -> None:
        stmt = update(AgentSessionORM).where(AgentSessionORM.id == session_id).values(
            last_active_at=datetime.utcnow()
        )
        await self.session.execute(stmt)
        await self.session.commit()

    async def save_message(self, message: AgentMessage) -> AgentMessage:
        db_msg = AgentMessageORM(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            query_pattern=message.query_pattern.value if message.query_pattern else "general",
            content=message.content,
            created_at=message.created_at
        )
        self.session.add(db_msg)
        
        # Save source URLs into agent_message_sources (1NF separation)
        if message.source_urls:
            for url in message.source_urls:
                db_source = AgentMessageSourceORM(
                    message_id=message.id,
                    source_url=url
                )
                self.session.add(db_source)
                
        await self.session.commit()
        await self.session.refresh(db_msg)
        return AgentMessage(
            id=db_msg.id,
            session_id=db_msg.session_id,
            role=db_msg.role,
            query_pattern=QueryPattern(db_msg.query_pattern),
            content=db_msg.content,
            source_urls=message.source_urls or [],
            created_at=db_msg.created_at
        )

    async def find_messages_by_session(self, session_id: UUID) -> list[AgentMessage]:
        query = select(AgentMessageORM).where(
            AgentMessageORM.session_id == session_id
        ).order_by(AgentMessageORM.created_at.desc()).limit(10)
        
        result = await self.session.execute(query)
        db_msgs = result.scalars().all()
        
        # Reverse list to return in chronological order (ASC)
        db_msgs = list(reversed(db_msgs))
        
        if not db_msgs:
            return []
            
        msg_ids = [m.id for m in db_msgs]
        sources_query = select(AgentMessageSourceORM).where(AgentMessageSourceORM.message_id.in_(msg_ids))
        sources_result = await self.session.execute(sources_query)
        db_sources = sources_result.scalars().all()
        
        sources_map = {}
        for s in db_sources:
            sources_map.setdefault(s.message_id, []).append(s.source_url)
            
        return [
            AgentMessage(
                id=m.id,
                session_id=m.session_id,
                role=m.role,
                query_pattern=QueryPattern(m.query_pattern),
                content=m.content,
                source_urls=sources_map.get(m.id, []),
                created_at=m.created_at
            ) for m in db_msgs
        ]

    async def save_satisfaction_feedback(self, message_id: UUID, is_positive: bool) -> None:
        query = select(SatisfactionFeedbackORM).where(SatisfactionFeedbackORM.message_id == message_id)
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.is_positive = is_positive
            existing.submitted_at = datetime.utcnow()
        else:
            new_fb = SatisfactionFeedbackORM(
                message_id=message_id,
                is_positive=is_positive,
                submitted_at=datetime.utcnow()
            )
            self.session.add(new_fb)
            
        await self.session.commit()

    async def find_satisfaction_feedback(self, message_id: UUID) -> Optional[bool]:
        query = select(SatisfactionFeedbackORM.is_positive).where(SatisfactionFeedbackORM.message_id == message_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def save_expert_feedback(self, message_id: UUID, expert_user_id: UUID, label: str, memo: Optional[str]) -> None:
        query = select(ExpertFeedbackORM).where(
            and_(ExpertFeedbackORM.message_id == message_id, ExpertFeedbackORM.expert_user_id == expert_user_id)
        )
        result = await self.session.execute(query)
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.label = label
            existing.memo = memo
            existing.submitted_at = datetime.utcnow()
        else:
            new_fb = ExpertFeedbackORM(
                message_id=message_id,
                expert_user_id=expert_user_id,
                label=label,
                memo=memo,
                submitted_at=datetime.utcnow()
            )
            self.session.add(new_fb)
            
        await self.session.commit()

    async def find_expert_feedback(self, message_id: UUID) -> Optional[dict]:
        query = select(ExpertFeedbackORM).where(ExpertFeedbackORM.message_id == message_id)
        result = await self.session.execute(query)
        db_fb = result.scalar_one_or_none()
        if db_fb:
            return {
                "id": db_fb.id,
                "message_id": db_fb.message_id,
                "expert_user_id": db_fb.expert_user_id,
                "label": db_fb.label,
                "memo": db_fb.memo,
                "submitted_at": db_fb.submitted_at
            }
        return None

    async def find_feedback_stats(self) -> list[dict]:
        # Group by query pattern join to get total feedbacks count and positive counts
        query = select(
            AgentMessageORM.query_pattern.label("chat_type"),
            func.count(SatisfactionFeedbackORM.id).label("total_count"),
            func.sum(case((SatisfactionFeedbackORM.is_positive == True, 1), else_=0)).label("positive_count")
        ).join(
            SatisfactionFeedbackORM, AgentMessageORM.id == SatisfactionFeedbackORM.message_id
        ).group_by(
            AgentMessageORM.query_pattern
        )
        
        result = await self.session.execute(query)
        rows = []
        for r in result.all():
            total = r.total_count
            pos = r.positive_count or 0
            # Convert positive/total count into average score out of 5 for backward compatibility with frontend
            avg_score = (pos / total) * 5 if total > 0 else 0
            rows.append({
                "chat_type": r.chat_type,
                "total_count": total,
                "avg_accuracy_score": avg_score,
                "avg_relevance_score": avg_score
            })
        return rows

    async def find_low_score_candidates(self, limit: int) -> list[dict]:
        # Aliases for self join to find preceding user message in the same session
        fb = SatisfactionFeedbackORM
        ans = aliased(AgentMessageORM)
        quest = aliased(AgentMessageORM)
        
        query = select(fb, ans, quest).join(
            ans, fb.message_id == ans.id
        ).join(
            quest,
            and_(
                quest.session_id == ans.session_id,
                quest.role == "user",
                quest.created_at < ans.created_at
            ),
            isouter=True
        ).where(
            fb.is_positive == False
        ).order_by(
            desc(fb.submitted_at), desc(quest.created_at)
        ).limit(limit)
        
        result = await self.session.execute(query)
        candidates = []
        seen_fb_ids = set()
        
        for fb_row, ans_row, quest_row in result.all():
            if fb_row.id in seen_fb_ids:
                continue
            seen_fb_ids.add(fb_row.id)
            candidates.append({
                "feedback_id": str(fb_row.id),
                "message_id": str(fb_row.message_id),
                "room_id": str(ans_row.session_id),  # mapped to room_id for backward compatibility
                "chat_type": ans_row.query_pattern,
                "accuracy_score": 2,  # legacy mock score for negative feedbacks
                "relevance_score": 2,
                "question": quest_row.content if quest_row else None,
                "answer": ans_row.content,
                "comment": "만족도 비추천 피드백",
                "created_at": fb_row.submitted_at
            })
            
        return candidates
