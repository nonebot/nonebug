from copy import deepcopy
from collections import defaultdict
from contextlib import contextmanager
from typing import (
    Dict,
    List,
    Type,
    Tuple,
    Union,
    Mapping,
    TypeVar,
    Iterator,
    KeysView,
    Optional,
    ItemsView,
    ValuesView,
    MutableMapping,
    overload,
)

from nonebot.matcher import Matcher, MatcherProvider

T = TypeVar("T")


class NoneBugProvider(MatcherProvider):  # pragma: no cover
    def __init__(self, matchers: Mapping[int, List[Type[Matcher]]]):
        self._matchers: Dict[int, List[Type[Matcher]]] = defaultdict(list, matchers)

        self._stack: List[Dict[int, List[Type[Matcher]]]] = []

    def __repr__(self) -> str:
        return f"NoneBugProvider(matchers={self._matchers!r})"

    def __contains__(self, o: object) -> bool:
        return o in self._matchers

    def __iter__(self) -> Iterator[int]:
        return iter(self._matchers)

    def __len__(self) -> int:
        return len(self._matchers)

    def __getitem__(self, key: int) -> List[Type["Matcher"]]:
        return self._matchers[key]

    def __setitem__(self, key: int, value: List[Type["Matcher"]]) -> None:
        self._matchers[key] = value

    def __delitem__(self, key: int) -> None:
        del self._matchers[key]

    def __eq__(self, other: object) -> bool:
        return self._matchers == other

    def keys(self) -> KeysView[int]:
        return self._matchers.keys()

    def values(self) -> ValuesView[List[Type["Matcher"]]]:
        return self._matchers.values()

    def items(self) -> ItemsView[int, List[Type["Matcher"]]]:
        return self._matchers.items()

    @overload
    def get(self, key: int) -> Optional[List[Type["Matcher"]]]: ...

    @overload
    def get(self, key: int, default: T) -> Union[List[Type["Matcher"]], T]: ...

    def get(
        self, key: int, default: Optional[T] = None
    ) -> Optional[Union[List[Type["Matcher"]], T]]:
        return self._matchers.get(key, default)

    def pop(self, key: int) -> List[Type["Matcher"]]:
        return self._matchers.pop(key)

    def popitem(self) -> Tuple[int, List[Type["Matcher"]]]:
        return self._matchers.popitem()

    def clear(self) -> None:
        self._matchers.clear()

    def update(self, __m: MutableMapping[int, List[Type["Matcher"]]]) -> None:
        self._matchers.update(__m)

    def setdefault(
        self, key: int, default: List[Type["Matcher"]]
    ) -> List[Type["Matcher"]]:
        return self._matchers.setdefault(key, default)

    @contextmanager
    def context(self, matchers: Optional[Mapping[int, List[Type[Matcher]]]] = None):
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
