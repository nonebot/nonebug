from copy import deepcopy
from typing import TypeVar, overload
from contextlib import contextmanager
from collections import defaultdict
from collections.abc import (
    Mapping,
    Iterator,
    KeysView,
    ItemsView,
    ValuesView,
    MutableMapping,
)

from nonebot.matcher import Matcher, MatcherProvider

T = TypeVar("T")


class NoneBugProvider(MatcherProvider):  # pragma: no cover
    def __init__(self, matchers: Mapping[int, list[type[Matcher]]]):
        self._matchers: dict[int, list[type[Matcher]]] = defaultdict(list, matchers)

        self._stack: list[dict[int, list[type[Matcher]]]] = []

    def __repr__(self) -> str:
        return f"NoneBugProvider(matchers={self._matchers!r})"

    def __contains__(self, o: object) -> bool:
        return o in self._matchers

    def __iter__(self) -> Iterator[int]:
        return iter(self._matchers)

    def __len__(self) -> int:
        return len(self._matchers)

    def __getitem__(self, key: int) -> list[type["Matcher"]]:
        return self._matchers[key]

    def __setitem__(self, key: int, value: list[type["Matcher"]]) -> None:
        self._matchers[key] = value

    def __delitem__(self, key: int) -> None:
        del self._matchers[key]

    def __eq__(self, other: object) -> bool:
        return self._matchers == other

    def keys(self) -> KeysView[int]:
        return self._matchers.keys()

    def values(self) -> ValuesView[list[type["Matcher"]]]:
        return self._matchers.values()

    def items(self) -> ItemsView[int, list[type["Matcher"]]]:
        return self._matchers.items()

    @overload
    def get(self, key: int) -> list[type["Matcher"]] | None: ...

    @overload
    def get(self, key: int, default: T) -> list[type["Matcher"]] | T: ...

    def get(
        self, key: int, default: T | None = None
    ) -> list[type["Matcher"]] | T | None:
        return self._matchers.get(key, default)

    def pop(self, key: int) -> list[type["Matcher"]]:  # type: ignore
        return self._matchers.pop(key)

    def popitem(self) -> tuple[int, list[type["Matcher"]]]:
        return self._matchers.popitem()

    def clear(self) -> None:
        self._matchers.clear()

    def update(self, m: MutableMapping[int, list[type["Matcher"]]], /) -> None:  # type: ignore
        self._matchers.update(m)

    def setdefault(
        self, key: int, default: list[type["Matcher"]]
    ) -> list[type["Matcher"]]:
        return self._matchers.setdefault(key, default)

    @contextmanager
    def context(self, matchers: Mapping[int, list[type[Matcher]]] | None = None):
        self._stack.append(self._matchers)
        self._matchers = (
            deepcopy(self._matchers)
            if matchers is None
            else defaultdict(list, matchers)
        )
        try:
            yield self
        finally:
            self._matchers = self._stack.pop()
