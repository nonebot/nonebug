from contextlib import AsyncExitStack
from typing import TYPE_CHECKING, Any, Dict, List, Type, Union, Optional, final

from nonebug.base import BaseApp

from .call_api import ApiContext

if TYPE_CHECKING:
    from nonebot.handler import Handler
    from nonebot.typing import T_Handler
    from nonebot.dependencies import Param


@final
class HandlerContext(ApiContext):
    def __init__(
        self,
        app: "HandlerMixin",
        handler: "Handler",
        kwargs: Dict[str, Any],
        *args,
        **_kwargs,
    ):
        super(HandlerContext, self).__init__(app, *args, **_kwargs)
        self.handler = handler
        self.kwargs = kwargs

    def should_return(self, result: Any) -> None:
        self.result = result

    async def run_test(self):
        stack = AsyncExitStack()
        async with stack:
            result = await self.handler(_stack=stack, **self.kwargs)
            if hasattr(self, "result"):
                assert result == self.result, "Handler return value mismatch"


class HandlerMixin(BaseApp):
    def test_handler(
        self,
        handler: Union["Handler", "T_Handler"],
        allow_types: Optional[List[Type["Param"]]] = None,
        **kwargs,
    ) -> HandlerContext:
        from nonebot.handler import Handler

        if not isinstance(handler, Handler):
            handler = Handler(handler, allow_types=allow_types)

        return HandlerContext(self, handler, kwargs)
