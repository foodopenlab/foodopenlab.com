from abc import ABC, abstractmethod

from braindead.app.dtos.watcher_dto import FilterQuery, FilterResult, WatcherQuery, WatcherResponse


class IWatcherPort(ABC):
    @abstractmethod
    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse: ...

    @abstractmethod
    async def filter_email(self, query: FilterQuery) -> FilterResult: ...
