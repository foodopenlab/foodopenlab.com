"""moneyball soccer erd with pgvector embeddings

Revision ID: 1e4fd7b6809c
Revises: 20260610_01
Create Date: 2026-07-14 02:49:17.810589

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e4fd7b6809c'
down_revision: Union[str, Sequence[str], None] = '20260610_01'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema — 축구 ERD 4개 테이블(stadium/team/schedule/player) + pgvector 임베딩 컬럼."""
    bind = op.get_bind()

    # 벡터 컬럼 테이블 생성 전에 익스텐션 보장 (이미 있으면 무시).
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    from matrix.grid_oracle_database_manager import Base
    import moneyball.adapter.outbound.orm.stadium_orm as stadium_orm
    import moneyball.adapter.outbound.orm.team_orm as team_orm
    import moneyball.adapter.outbound.orm.schedule_orm as schedule_orm
    import moneyball.adapter.outbound.orm.player_orm as player_orm

    # ORM 메타데이터로 신규 테이블만 생성(checkfirst=True 기본 — 기존 테이블은 건너뜀).
    # FK 의존성 순서는 create_all이 자동 정렬한다.
    Base.metadata.create_all(
        bind,
        tables=[
            stadium_orm.StadiumORM.__table__,
            team_orm.TeamORM.__table__,
            schedule_orm.ScheduleORM.__table__,
            player_orm.PlayerORM.__table__,
        ],
    )


def downgrade() -> None:
    """Downgrade schema — FK 역순으로 4개 테이블 삭제."""
    op.drop_table("player")
    op.drop_table("schedule")
    op.drop_table("team")
    op.drop_table("stadium")
