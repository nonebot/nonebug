from typing import TYPE_CHECKING, Any, Dict, Union

from .fake import make_fake_classes

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment


class App:
    def __init__(self):
        self.Adapter, self.Bot = make_fake_classes()

    def should_call_api(self, api: str, data: Dict[str, Any]):
        ...

    def should_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ):
        ...

    def got_call_api(self, api: str, data: Dict[str, Any]) -> Any:
        ...

    def got_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ) -> Any:
        ...
