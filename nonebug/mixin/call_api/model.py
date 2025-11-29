from typing import TYPE_CHECKING, Any, Union, Optional
from dataclasses import dataclass

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment


@dataclass
class Model: ...


@dataclass
class Api(Model):
    name: str
    data: dict[str, Any]
    result: Any
    exception: Optional[Exception]
    adapter: Optional["Adapter"]


@dataclass
class Send(Model):
    event: "Event"
    message: Union[str, "Message", "MessageSegment"]
    kwargs: dict[str, Any]
    result: Any
    exception: Optional[Exception]
    bot: Optional["Bot"]
