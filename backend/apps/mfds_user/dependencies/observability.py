from typing import Any, cast
from fastapi import Depends
from matrix.grid_oracle_database_manager import AsyncSessionLocal
from mfds_user.app.ports.output.observability_ports import SearchLoggerPort
from mfds_user.adapter.outbound.observability.observability_adapter import SearchLoggerAdapter

def get_search_logger() -> SearchLoggerPort:
    return SearchLoggerAdapter(session_factory=cast(Any, AsyncSessionLocal))
