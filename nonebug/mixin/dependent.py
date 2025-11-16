from typing_extensions import final
from collections.abc import Iterable
from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Union
from collections.abc import Callable

import pytest

from nonebug.base import BaseApp

from .call_api import ApiContext

if TYPE_CHECKING:
    from nonebot.dependencies import Param, Dependent


UNSET = object()


@final
class DependentContext(ApiContext):
    def __init__(
        self,
        app: "DependentMixin",
        *args,
        dependent: "Dependent",
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.dependent = dependent
        self.kwargs: dict[str, Any] = {}

    def pass_params(self, **kwargs: Any) -> None:
        self.kwargs.update(kwargs)

    def should_return(self, result: Any) -> None:
        self.result = result

    async def run(self):
        stack = AsyncExitStack()
        async with stack:
            result = await self.dependent(stack=stack, **self.kwargs)
            if (
                expected := getattr(self, "result", UNSET)
            ) is not UNSET and result != expected:
                pytest.fail(
                    f"Dependent got return value {result!r} but expected {expected!r}"
                )


class DependentMixin(BaseApp):
    def test_dependent(
        self,
        dependent: Union["Dependent", Callable[..., Any]],
        allow_types: Iterable[type["Param"]] | None = None,
        parameterless: Iterable[Any] | None = None,
    ) -> DependentContext:
        from nonebot.dependencies import Dependent

        if not isinstance(dependent, Dependent):
            dependent = Dependent[Any].parse(
                call=dependent,
                parameterless=parameterless,
                allow_types=allow_types or (),
            )

        return DependentContext(self, dependent=dependent)

    test_handler = test_dependent
