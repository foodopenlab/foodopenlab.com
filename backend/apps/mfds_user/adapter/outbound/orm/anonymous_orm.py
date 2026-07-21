from uuid import UUID
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from matrix.orm.user_orm import UserORM

class AnonymousORM(UserORM):
    __tablename__ = "anonymous"

    id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    cookie_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "anonymous",
    }
