from abc import ABC, abstractmethod

from braindead.adapter.inbound.api.schemas.watcher_schema import WatcherSchema
from braindead.app.dtos.watcher_dto import FilterResult, WatcherResponse


class IWatcherUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, schema: WatcherSchema) -> WatcherResponse: ...

    @abstractmethod
    async def filter_email(self, text: str) -> FilterResult: ...
