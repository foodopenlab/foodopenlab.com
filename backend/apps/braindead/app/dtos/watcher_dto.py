from dataclasses import dataclass


@dataclass
class WatcherQuery:
    id: int
    name: str


@dataclass
class WatcherResponse:
    id: int
    name: str


@dataclass
class FilterQuery:
    text: str


@dataclass
class FilterResult:
    label: int  # 0=정상, 1=차단
    is_normal: bool
