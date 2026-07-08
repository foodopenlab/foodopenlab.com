"""titanic ORM 컬럼 타입을 스키마(int/float/str)에 맞춤

Revision ID: 20260604_02
Revises: 20260604_01
Create Date: 2026-06-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "20260604_02"
down_revision: Union[str, None] = "20260604_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("titanic_bookings")
    op.drop_table("titanic_persons")
    op.create_table(
        "titanic_persons",
        sa.Column("passenger_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("age", sa.Float(), nullable=True),
        sa.Column("sib_sp", sa.Integer(), nullable=True),
        sa.Column("parch", sa.Integer(), nullable=True),
        sa.Column("survived", sa.String(length=16), nullable=True),
        sa.PrimaryKeyConstraint("passenger_id"),
    )
    op.create_table(
        "titanic_bookings",
        sa.Column("passenger_id", sa.Integer(), nullable=False),
        sa.Column("pclass", sa.Integer(), nullable=True),
        sa.Column("ticket", sa.String(length=64), nullable=True),
        sa.Column("fare", sa.Float(), nullable=True),
        sa.Column("cabin", sa.String(length=64), nullable=True),
        sa.Column("embarked", sa.String(length=8), nullable=True),
        sa.ForeignKeyConstraint(
            ["passenger_id"],
            ["titanic_persons.passenger_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("passenger_id"),
    )


def downgrade() -> None:
    op.drop_table("titanic_bookings")
    op.drop_table("titanic_persons")
    op.create_table(
        "titanic_persons",
        sa.Column("passenger_id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("gender", sa.String(length=32), nullable=True),
        sa.Column("age", sa.String(length=32), nullable=True),
        sa.Column("sib_sp", sa.String(length=32), nullable=True),
        sa.Column("parch", sa.String(length=32), nullable=True),
        sa.Column("survived", sa.String(length=16), nullable=True),
        sa.PrimaryKeyConstraint("passenger_id"),
    )
    op.create_table(
        "titanic_bookings",
        sa.Column("passenger_id", sa.String(length=32), nullable=False),
        sa.Column("pclass", sa.String(length=16), nullable=True),
        sa.Column("ticket", sa.String(length=64), nullable=True),
        sa.Column("fare", sa.String(length=32), nullable=True),
        sa.Column("cabin", sa.String(length=64), nullable=True),
        sa.Column("embarked", sa.String(length=8), nullable=True),
        sa.ForeignKeyConstraint(
            ["passenger_id"],
            ["titanic_persons.passenger_id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("passenger_id"),
    )
