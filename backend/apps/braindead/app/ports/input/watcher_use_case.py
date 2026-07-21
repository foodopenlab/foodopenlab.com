from abc import ABC, abstractmethod

from braindead.app.dtos.watcher_dto import FilterResult, WatcherQuery, WatcherResponse


class IWatcherUseCase(ABC):
    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse: ...

    @abstractmethod
    async def filter_email(self, text: str) -> FilterResult: ...
