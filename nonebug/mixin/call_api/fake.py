from typing_extensions import override
from typing import TYPE_CHECKING, Any, Type, Union, TypeVar, Optional, overload

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

    from . import ApiContext

A = TypeVar("A", bound=Type["Adapter"])
B = TypeVar("B", bound=Type["Bot"])


@overload
def make_fake_adapter(ctx: "ApiContext", base: None = None) -> Type["Adapter"]: ...


@overload
def make_fake_adapter(ctx: "ApiContext", base: A) -> A: ...


# fake class should be created every init
def make_fake_adapter(
    ctx: "ApiContext", base: Optional[A] = None
) -> Union[A, Type["Adapter"]]:
    from nonebot.adapters import Adapter

    _base = base or Adapter

    class FakeAdapter(_base):  # type: ignore
        @classmethod
        @override
        def get_name(cls) -> str:
            return "fake"

        @override
        async def _call_api(self, bot: "Bot", api: str, **data) -> Any:
            return ctx.got_call_api(self, api, **data)

    return FakeAdapter


@overload
def make_fake_bot(ctx: "ApiContext", base: None = None) -> Type["Bot"]: ...


@overload
def make_fake_bot(ctx: "ApiContext", base: B) -> B: ...


def make_fake_bot(ctx: "ApiContext", base: Optional[B] = None) -> Union[B, Type["Bot"]]:
    from nonebot.adapters import Bot

    _base = base or Bot

    class FakeBot(_base):  # type: ignore
        @override
        async def send(
            self,
            event: "Event",
            message: Union[str, "Message", "MessageSegment"],
            **kwargs,
        ) -> Any:
            return ctx.got_call_send(self, event, message, **kwargs)

    return FakeBot
