"""apply_erd_v10

Revision ID: e97b22871765
Revises: 20260604_02
Create Date: 2026-06-10 11:27:00.873251

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e97b22871765'
down_revision: Union[str, Sequence[str], None] = '20260604_02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


from sqlalchemy import inspect
from uuid import UUID

def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    
    # 1. If users table does not exist, create all missing tables from ORM metadata
    if "users" not in tables:
        from matrix.grid_oracle_database_manager import Base
        from sqlmodel import SQLModel
        import mfds_user.adapter.outbound.orm
        import mfds_admin.adapter.outbound.orm
        
        Base.metadata.create_all(bind)
        SQLModel.metadata.create_all(bind)
        print("Created all missing tables from ORM metadata.")
        
    # Refresh tables list
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    
    # 2. Check and migrate expert_users, admins, anonymous to JTI if needed
    if "users" in tables:
        user_count = bind.execute(sa.text("SELECT count(*) FROM users")).scalar()
        if user_count == 0:
            for child_table, user_type in [("admins", "admin"), ("expert_users", "expert"), ("anonymous", "anonymous")]:
                if child_table in tables:
                    bind.execute(sa.text(
                        f"INSERT INTO users (id, user_type, created_at) "
                        f"SELECT id, '{user_type}', COALESCE(created_at, NOW()) FROM {child_table} "
                        f"ON CONFLICT DO NOTHING"
                    ))
            print("Populated parent 'users' table from existing records.")

    # 3. Add JTI foreign key constraints if they don't exist
    for child_table in ["admins", "expert_users", "anonymous"]:
        if child_table in tables:
            fks = inspector.get_foreign_keys(child_table)
            has_fk_to_users = any(fk['referred_table'] == 'users' for fk in fks)
            if not has_fk_to_users:
                op.create_foreign_key(None, child_table, 'users', ['id'], ['id'], ondelete='CASCADE')
                print(f"Added JTI foreign key constraint for {child_table}")

    # For agent_sessions -> users
    if "agent_sessions" in tables:
        fks = inspector.get_foreign_keys("agent_sessions")
        has_fk_to_users = any(fk['referred_table'] == 'users' for fk in fks)
        if not has_fk_to_users:
            op.create_foreign_key(None, "agent_sessions", 'users', ['actor_id'], ['id'], ondelete='CASCADE')
            print("Added foreign key constraint for agent_sessions")

    # Drop columns if they exist
    for table_name, col_name in [
        ("agent_messages", "source_urls"),
        ("agent_sessions", "actor_type"),
        ("anonymous", "created_at"),
        ("expert_users", "created_at")
    ]:
        if table_name in tables:
            cols = [c["name"] for c in inspector.get_columns(table_name)]
            if col_name in cols:
                op.drop_column(table_name, col_name)
                print(f"Dropped column {col_name} from {table_name}")


def downgrade() -> None:
    """Downgrade schema."""
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()
    
    # 1. Restore columns if they don't exist
    for table_name, col_name, col_type in [
        ("agent_messages", "source_urls", postgresql.ARRAY(sa.TEXT())),
        ("agent_sessions", "actor_type", sa.VARCHAR(length=20)),
        ("anonymous", "created_at", sa.TIMESTAMP(timezone=True)),
        ("expert_users", "created_at", sa.TIMESTAMP(timezone=True))
    ]:
        if table_name in tables:
            cols = [c["name"] for c in inspector.get_columns(table_name)]
            if col_name not in cols:
                if col_name == "created_at":
                    op.add_column(table_name, sa.Column(col_name, col_type, nullable=True))
                    bind.execute(sa.text(f"UPDATE {table_name} SET created_at = NOW()"))
                    op.alter_column(table_name, col_name, nullable=False)
                elif col_name == "actor_type":
                    op.add_column(table_name, sa.Column(col_name, col_type, nullable=True))
                    bind.execute(sa.text(
                        "UPDATE agent_sessions s SET actor_type = u.user_type "
                        "FROM users u WHERE s.actor_id = u.id"
                    ))
                    bind.execute(sa.text("UPDATE agent_sessions SET actor_type = 'expert' WHERE actor_type IS NULL"))
                    op.alter_column(table_name, col_name, nullable=False)
                else:
                    op.add_column(table_name, sa.Column(col_name, col_type, nullable=True))
                print(f"Restored column {col_name} in {table_name}")

    # 2. Drop JTI constraints if they exist
    for child_table in ["admins", "expert_users", "anonymous"]:
        if child_table in tables:
            fks = inspector.get_foreign_keys(child_table)
            fk_name = None
            for fk in fks:
                if fk['referred_table'] == 'users':
                    fk_name = fk['name']
                    break
            if fk_name:
                op.drop_constraint(fk_name, child_table, type_='foreignkey')
                print(f"Dropped JTI foreign key constraint {fk_name} for {child_table}")

    # Drop agent_sessions -> users constraint
    if "agent_sessions" in tables:
        fks = inspector.get_foreign_keys("agent_sessions")
        fk_name = None
        for fk in fks:
            if fk['referred_table'] == 'users':
                fk_name = fk['name']
                break
        if fk_name:
            op.drop_constraint(fk_name, "agent_sessions", type_='foreignkey')
            print(f"Dropped foreign key constraint {fk_name} for agent_sessions")
