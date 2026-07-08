from uuid import UUID, uuid4
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from matrix.grid_oracle_database_manager import Base

class CategoryKeywordORM(Base):
    __tablename__ = "category_keywords"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    category_code: Mapped[str] = mapped_column(String(255), ForeignKey("industry_category.code", ondelete="CASCADE"), nullable=False)
    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
