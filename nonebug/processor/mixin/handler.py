from contextlib import AsyncExitStack
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    List,
    Type,
    Union,
    TypeVar,
    Optional,
)

from nonebug.base import BaseApp, Context

if TYPE_CHECKING:
    from nonebot.handler import Handler
    from nonebot.typing import T_Handler
    from nonebot.dependencies import Param


T = TypeVar("T", bound="HandlerMixin")


class HandlerContext(Context[T]):
    def __init__(self, app: T, handler: "Handler", kwargs: Dict[str, Any]):
        super(HandlerContext, self).__init__(app)
        self.handler = handler
        self.kwargs = kwargs

    def should_return(self, result: Any):
        self.result = result

    async def run_test(self):
        stack = AsyncExitStack()
        async with stack:
            result = await self.handler(_stack=stack, **self.kwargs)
            if hasattr(self, "result"):
                assert result == self.result, "Handler return value mismatch"


class HandlerMixin(BaseApp):
    def test_handler(
        self: T,
        handler: Union["Handler", "T_Handler"],
        allow_types: Optional[List[Type["Param"]]] = None,
        **kwargs,
    ) -> HandlerContext[T]:
        from nonebot.handler import Handler

        if not isinstance(handler, Handler):
            handler = Handler(handler, allow_types=allow_types)

        return HandlerContext(self, handler, kwargs)

    def should_return(self, result: Any) -> None:
        assert isinstance(
            self.context, HandlerContext
        ), "Return value assertion should be used in handler test"
        self.context.should_return(result)
