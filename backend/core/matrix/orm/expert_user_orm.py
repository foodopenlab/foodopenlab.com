from uuid import UUID
from datetime import datetime
from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from matrix.orm.user_orm import UserORM

class ExpertUserORM(UserORM):
    __tablename__ = "expert_users"

    id: Mapped[UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    picture: Mapped[str | None] = mapped_column(String(500), nullable=True)
    auth_provider: Mapped[str] = mapped_column(String(20), default="email", nullable=False)  # 'email' | 'google' | 'kakao' | 'naver'
    oauth_provider_id: Mapped[str | None] = mapped_column(String(255), index=True, nullable=True)  # 소셜 제공사 고유 subject
    hashed_password: Mapped[str | None] = mapped_column(String(255), nullable=True)
    last_login: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "expert",
    }
