from fastapi import Depends

from braindead.adapter.outbound.repositories.watcher_repository import WatcherRepository
from braindead.app.ports.input.watcher_use_case import IWatcherUseCase
from braindead.app.ports.output.watcher_port import IWatcherPort
from braindead.app.use_cases.watcher_interactor import WatcherInteractor


def get_watcher_port() -> IWatcherPort:
    return WatcherRepository()


def get_watcher_use_case(
    port: IWatcherPort = Depends(get_watcher_port),
) -> IWatcherUseCase:
    return WatcherInteractor(port=port)
