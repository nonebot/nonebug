from typing import TYPE_CHECKING, Any, Type, Union, Optional

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

    from . import ApiContext


# fake class should be created every init
def make_fake_adapter(ctx: "ApiContext", base: Optional[Type["Adapter"]] = None):
    from nonebot.adapters import Adapter
    from nonebot.typing import overrides

    base = base or Adapter

    class FakeAdapter(base):
        @classmethod
        @overrides(base)
        def get_name(cls) -> str:
            return "fake"

        @overrides(base)
        async def _call_api(self, bot: "Bot", api: str, **data) -> Any:
            return ctx.got_call_api(self, api, **data)

    return FakeAdapter


def make_fake_bot(ctx: "ApiContext", base: Optional[Type["Bot"]] = None) -> Type["Bot"]:
    from nonebot.adapters import Bot
    from nonebot.typing import overrides

    base = base or Bot

    class FakeBot(base):
        @overrides(base)
        async def send(
            self,
            event: "Event",
            message: Union[str, "Message", "MessageSegment"],
            **kwargs,
        ) -> Any:
            return ctx.got_call_send(self, event, message, **kwargs)

    return FakeBot
