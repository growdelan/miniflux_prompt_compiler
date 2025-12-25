from dataclasses import dataclass
from typing import TypedDict


class MinifluxEntry(TypedDict, total=False):
    id: int | str | None
    title: str | None
    url: str | None


@dataclass
class ProcessedItem:
    title: str
    content: str


class ContentFetchError(RuntimeError):
    pass


class MinifluxError(RuntimeError):
    pass
