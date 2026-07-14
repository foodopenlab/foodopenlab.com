"""Alembic migration environment — SQLAlchemy 2.0 + matrix.grid_oracle_database_manager.Base."""

from __future__ import annotations

import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# com.auditor/ 루트·apps 패키지 (titanic 등)
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_CORE_DIR = _BACKEND_DIR / "core"
_APPS_DIR = _BACKEND_DIR / "apps"
for path in (_BACKEND_DIR, _CORE_DIR, _APPS_DIR):
    if path.is_dir() and str(path) not in sys.path:
        sys.path.insert(0, str(path))

from matrix.grid_oracle_database_manager import SYNC_DATABASE_URL, Base  # noqa: E402

# ORM 모델 import → Base.metadata에 테이블 등록
import titanic.adapter.outbound.orm.passenger_jack_trainer_orm  # noqa: F401, E402
import titanic.adapter.outbound.orm.titanic_booking_orm  # noqa: F401, E402
import titanic.adapter.outbound.orm.crew_smith_captain_orm  # noqa: F401, E402
import mfds_user.adapter.outbound.orm  # noqa: F401, E402
import mfds_admin.adapter.outbound.orm  # noqa: F401, E402
import moneyball.adapter.outbound.orm.stadium_orm  # noqa: F401, E402
import moneyball.adapter.outbound.orm.team_orm  # noqa: F401, E402
import moneyball.adapter.outbound.orm.schedule_orm  # noqa: F401, E402
import moneyball.adapter.outbound.orm.player_orm  # noqa: F401, E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from sqlmodel import SQLModel
target_metadata = [Base.metadata, SQLModel.metadata]

if SYNC_DATABASE_URL:
    config.set_main_option("sqlalchemy.url", SYNC_DATABASE_URL)


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
