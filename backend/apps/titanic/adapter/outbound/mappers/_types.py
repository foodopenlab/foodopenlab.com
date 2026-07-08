"""Outbound persistence row types — ORM upsert용 plain dict (인프라 경계)."""

from __future__ import annotations

from typing import TypeAlias

PersonPersistenceRow: TypeAlias = dict[str, int | float | str | None]
BookingPersistenceRow: TypeAlias = dict[str, int | float | str | None]
