from braindead.app.dtos.watcher_dto import FilterQuery, FilterResult, WatcherQuery, WatcherResponse
from braindead.app.ports.input.watcher_use_case import IWatcherUseCase
from braindead.app.ports.output.watcher_port import IWatcherPort


class WatcherInteractor(IWatcherUseCase):
    def __init__(self, port: IWatcherPort) -> None:
        self._port = port

    async def introduce_myself(self, query: WatcherQuery) -> WatcherResponse:
        return await self._port.introduce_myself(query)

    async def filter_email(self, text: str) -> FilterResult:
        return await self._port.filter_email(FilterQuery(text=text))
