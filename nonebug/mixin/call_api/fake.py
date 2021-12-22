from typing import TYPE_CHECKING, Any, Type, Union, Optional

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Adapter

    from . import ApiContext


# fake class should be created every init
def make_fake_adapter(base: Optional[Type["Adapter"]] = None):
    from nonebot.drivers import Driver
    from nonebot.typing import overrides
    from nonebot.adapters import Bot, Adapter

    base = base or Adapter

    class FakeAdapter(base):
        @overrides(base)
        def __init__(self, driver: Driver, ctx: "ApiContext", **kwargs: Any):
            super(FakeAdapter, self).__init__(driver, **kwargs)
            self.ctx = ctx

        @classmethod
        @overrides(base)
        def get_name(cls) -> str:
            return "fake"

        @overrides(base)
        async def _call_api(self, bot: Bot, api: str, **data) -> Any:
            return self.ctx.got_call_api(api, **data)

    return FakeAdapter


def make_fake_bot(base: Optional[Type["Bot"]] = None) -> Type["Bot"]:
    from nonebot.typing import overrides
    from nonebot.adapters import Bot, Event, Message, MessageSegment

    base = base or Bot

    class FakeBot(base):
        @property
        def ctx(self) -> "ApiContext":
            return self.adapter.ctx  # type: ignore

        @overrides(base)
        async def send(
            self,
            event: "Event",
            message: Union[str, "Message", "MessageSegment"],
            **kwargs,
        ) -> Any:
            return self.ctx.got_call_send(event, message, **kwargs)

    return FakeBot
