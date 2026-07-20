"""expert_users에 소셜 OAuth subject 컬럼(oauth_provider_id) 추가

Revision ID: 20260720_01
Revises: 1e4fd7b6809c
Create Date: 2026-07-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260720_01"
down_revision: Union[str, None] = "1e4fd7b6809c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "expert_users",
        sa.Column("oauth_provider_id", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_expert_users_oauth_provider_id",
        "expert_users",
        ["oauth_provider_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_expert_users_oauth_provider_id", table_name="expert_users")
    op.drop_column("expert_users", "oauth_provider_id")
