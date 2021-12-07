from queue import Queue
from typing import TYPE_CHECKING, Any, Dict, Union

from .fake import make_fake_classes
from .model import Api, Send, Model

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment


class App:
    def __init__(self):
        self.Adapter, self.Bot = make_fake_classes()
        self.wait_list: Queue[Model] = Queue()

    def should_call_api(self, api: str, data: Dict[str, Any], result: Any) -> Api:
        model = Api(name=api, data=data, result=result)
        self.wait_list.put(model)
        return model

    def should_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ) -> Send:
        model = Send(event=event, message=message, kwargs=kwargs)
        self.wait_list.put(model)
        return model

    def got_call_api(self, api: str, data: Dict[str, Any]) -> Any:
        model = self.wait_list.get()
        assert isinstance(
            model, Api
        ), f"Application got api call {api} but expected {model}"
        assert (
            model.name == api
        ), f"Application got api call {api} but expected {model.name}"
        assert (
            model.data == data
        ), f"Application got api call {api} with data {data} but expected {model.data}"

    def got_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ) -> Any:
        model = self.wait_list.get()
        assert isinstance(
            model, Send
        ), f"Application got send call but expected {model}"
        assert (
            model.event.dict() == event.dict()
        ), f"Application got send call with event {event} but expected {model.event}"
        assert (
            model.message == message
        ), f"Application got send call with message {message} but expected {model.message}"
        assert (
            model.kwargs == kwargs
        ), f"Application got send call with kwargs {kwargs} but expected {model.kwargs}"
