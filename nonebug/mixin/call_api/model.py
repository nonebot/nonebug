from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict, Union, Optional

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment


@dataclass
class Model:
    ...


@dataclass
class Api(Model):
    name: str
    data: Dict[str, Any]
    result: Any
    adapter: Optional["Adapter"]


@dataclass
class Send(Model):
    event: "Event"
    message: Union[str, "Message", "MessageSegment"]
    kwargs: Dict[str, Any]
    result: Any
    bot: Optional["Bot"]
