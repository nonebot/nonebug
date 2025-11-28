from typing import TYPE_CHECKING, Any, Union, TypeVar, overload
from typing_extensions import override

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

    from . import ApiContext

A = TypeVar("A", bound=type["Adapter"])
B = TypeVar("B", bound=type["Bot"])


@overload
def make_fake_adapter(ctx: "ApiContext", base: None = None) -> type["Adapter"]: ...


@overload
def make_fake_adapter(ctx: "ApiContext", base: A) -> A: ...


# fake class should be created every init
def make_fake_adapter(ctx: "ApiContext", base: A | None = None) -> A | type["Adapter"]:
    from nonebot.adapters import Adapter

    _base = base or Adapter

    class FakeAdapter(_base):  # type: ignore
        @classmethod
        @override
        def get_name(cls) -> str:  # type: ignore
            return "fake"

        @override
        async def _call_api(self, bot: "Bot", api: str, **data) -> Any:  # type: ignore
            return ctx.got_call_api(self, api, **data)

    return FakeAdapter


@overload
def make_fake_bot(ctx: "ApiContext", base: None = None) -> type["Bot"]: ...


@overload
def make_fake_bot(ctx: "ApiContext", base: B) -> B: ...


def make_fake_bot(ctx: "ApiContext", base: B | None = None) -> B | type["Bot"]:
    from nonebot.adapters import Bot

    _base = base or Bot

    class FakeBot(_base):  # type: ignore
        @override
        async def send(  # type: ignore
            self,
            event: "Event",
            message: Union[str, "Message", "MessageSegment"],
            **kwargs,
        ) -> Any:
            return ctx.got_call_send(self, event, message, **kwargs)

    return FakeBot
