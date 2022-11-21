from typing_extensions import final
from contextlib import AsyncExitStack
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    Union,
    Callable,
    Iterable,
    Optional,
)

from nonebug.base import BaseApp

from .call_api import ApiContext

if TYPE_CHECKING:
    from nonebot.dependencies import Param, Dependent


@final
class DependentContext(ApiContext):
    def __init__(
        self,
        app: "DependentMixin",
        *args,
        dependent: "Dependent",
        **kwargs,
    ):
        super(DependentContext, self).__init__(app, *args, **kwargs)
        self.dependent = dependent
        self.kwargs: Dict[str, Any] = {}

    def pass_params(self, **kwargs: Any) -> None:
        self.kwargs.update(kwargs)

    def should_return(self, result: Any) -> None:
        self.result = result

    async def run_test(self):
        stack = AsyncExitStack()
        async with stack:
            result = await self.dependent(stack=stack, **self.kwargs)
            if hasattr(self, "result"):
                assert result == self.result, "Handler return value mismatch"


class DependentMixin(BaseApp):
    def test_dependent(
        self,
        dependent: Union["Dependent", Callable[..., Any]],
        allow_types: Optional[Iterable[Type["Param"]]] = None,
        parameterless: Optional[Iterable[Any]] = None,
    ) -> DependentContext:
        from nonebot.dependencies import Dependent

        if not isinstance(dependent, Dependent):
            dependent = Dependent[Any].parse(
                call=dependent,
                parameterless=parameterless,
                allow_types=allow_types or tuple(),
            )

        return DependentContext(self, dependent=dependent)

    test_handler = test_dependent
