import uuid
from typing import Optional, Any
from mfds_user.app.ports.input.chat_use_case import ChatUseCase
from mfds_user.app.ports.output.chat_repository import ChatRepository
from mfds_user.app.ports.output.anonymous_repository import AnonymousRepository
from mfds_user.app.ports.output.llm_port import LlmPort
from mfds_user.app.dtos.chat_dto import ChatPersistDTO, ChatRequestDTO, ChatResponseDTO
from mfds_user.domain.entities.agent_message_entity import AgentMessage
from mfds_user.domain.value_objects.query_pattern_vo import QueryPattern, classify_pattern

class ChatInteractor(ChatUseCase):
    def __init__(
        self,
        chat_repository: ChatRepository,
        anonymous_repository: AnonymousRepository,
        llm_port: LlmPort
    ) -> None:
        self._chat_repository = chat_repository
        self._anonymous_repository = anonymous_repository
        self._llm_port = llm_port

    @staticmethod
    def _resolve_query_pattern(raw: str | None, message: str) -> QueryPattern:
        if raw:
            try:
                return QueryPattern(raw)
            except ValueError:
                pass
        return classify_pattern(message)

    async def _ensure_session(
        self,
        session_key: str,
        actor_id: Optional[uuid.UUID] = None,
        actor_type: Optional[str] = None,
    ) -> uuid.UUID:
        session_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, session_key)
        session = await self._chat_repository.find_session(session_uuid)
        if not session:
            resolved_actor_type = actor_type or "anonymous"
            resolved_actor_id = actor_id
            if not resolved_actor_id:
                anon = await self._anonymous_repository.find_by_cookie_id(session_key)
                if not anon:
                    anon = await self._anonymous_repository.create_anonymous(session_key)
                resolved_actor_id = anon.id
            assert resolved_actor_id is not None
            await self._chat_repository.create_session(session_uuid, resolved_actor_type, resolved_actor_id)
        await self._chat_repository.update_session_active(session_uuid)
        return session_uuid

    async def handle_chat(self, request: ChatRequestDTO) -> ChatResponseDTO:
        session_uuid = await self._ensure_session(
            request.session_key,
            actor_id=request.actor_id,
            actor_type=request.actor_type,
        )

        # Classify query pattern and save user message
        query_pattern = classify_pattern(request.message)
        user_msg = AgentMessage(
            id=uuid.uuid4(),
            session_id=session_uuid,
            role="user",
            query_pattern=query_pattern,
            content=request.message
        )
        await self._chat_repository.save_message(user_msg)

        # 4. Invoke LLM Adapter via LlmPort
        history_lines = [(item.role, item.content) for item in request.history]
        reply = await self._llm_port.generate_reply(request.message, history_lines)

        # 5. Save assistant response
        ai_msg_id = uuid.uuid4()
        ai_msg = AgentMessage(
            id=ai_msg_id,
            session_id=session_uuid,
            role="assistant",
            query_pattern=query_pattern,
            content=reply
        )
        await self._chat_repository.save_message(ai_msg)

        return ChatResponseDTO(
            reply=reply,
            session_key=request.session_key,
            message_id=str(ai_msg_id)
        )

    async def persist_exchange(self, request: ChatPersistDTO) -> ChatResponseDTO:
        session_uuid = await self._ensure_session(
            request.session_key,
            actor_id=request.actor_id,
            actor_type=request.actor_type,
        )
        query_pattern = self._resolve_query_pattern(request.query_pattern, request.user_message)

        user_msg = AgentMessage(
            id=uuid.uuid4(),
            session_id=session_uuid,
            role="user",
            query_pattern=query_pattern,
            content=request.user_message,
        )
        await self._chat_repository.save_message(user_msg)

        ai_msg_id = uuid.uuid4()
        ai_msg = AgentMessage(
            id=ai_msg_id,
            session_id=session_uuid,
            role="assistant",
            query_pattern=query_pattern,
            content=request.assistant_message,
        )
        await self._chat_repository.save_message(ai_msg)

        return ChatResponseDTO(
            reply=request.assistant_message,
            session_key=request.session_key,
            message_id=str(ai_msg_id),
        )

    async def save_legacy_feedback(self, message_id: uuid.UUID, session_key: str, accuracy_score: int, relevance_score: int) -> None:
        # Map legacy scores to is_positive: if average score is >= 4, it is positive (👍)
        is_positive = (accuracy_score + relevance_score) >= 8
        await self._chat_repository.save_satisfaction_feedback(message_id, is_positive)

    async def get_legacy_feedback(self, message_id: uuid.UUID, session_key: str) -> Optional[dict]:
        is_positive = await self._chat_repository.find_satisfaction_feedback(message_id)
        if is_positive is None:
            return None
        # Convert back to legacy format for frontend consumption
        score = 5 if is_positive else 2
        return {
            "accuracy_score": score,
            "relevance_score": score
        }

    async def save_satisfaction_feedback(self, message_id: uuid.UUID, is_positive: bool) -> None:
        await self._chat_repository.save_satisfaction_feedback(message_id, is_positive)

    async def save_expert_feedback(self, message_id: uuid.UUID, expert_user_id: uuid.UUID, label: str, memo: Optional[str]) -> None:
        if label not in ("correct", "partial", "incorrect"):
            raise ValueError("올바르지 않은 라벨 형태입니다.")
        await self._chat_repository.save_expert_feedback(message_id, expert_user_id, label, memo)

    async def get_feedback_stats(self) -> list[dict]:
        return await self._chat_repository.find_feedback_stats()

    async def get_low_score_candidates(self, limit: int = 100) -> list[dict]:
        return await self._chat_repository.find_low_score_candidates(limit)
