from uuid import UUID, uuid4
from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class AgentMessageSourceORM(Base):
    __tablename__ = "agent_message_sources"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("agent_messages.id", ondelete="CASCADE"), nullable=False)
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
