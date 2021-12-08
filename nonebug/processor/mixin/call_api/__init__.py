from queue import Queue
from typing import TYPE_CHECKING, Any, Dict, Union

from nonebug.base import BaseApp, Context

from .model import Api, Send, Model

if TYPE_CHECKING:
    from nonebot.adapters import Event, Message, MessageSegment


class ApiContext(Context):
    def __init__(self, app: BaseApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.wait_list: Queue[Model] = Queue()

    def should_call_api(self, api: str, data: Dict[str, Any], result: Any) -> Api:
        model = Api(name=api, data=data, result=result)
        self.wait_list.put(model)
        return model

    def should_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        result: Any,
        **kwargs: Any,
    ) -> Send:
        model = Send(event=event, message=message, kwargs=kwargs, result=result)
        self.wait_list.put(model)
        return model

    def got_call_api(self, api: str, data: Dict[str, Any]) -> Any:
        assert (
            not self.wait_list.empty()
        ), f"Application has no api call but expected api={api} data={data}"
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
        return model.result

    def got_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ) -> Any:
        assert (
            not self.wait_list.empty()
        ), f"Application has no api call but expected event={event} message={message} kwargs={kwargs}"
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
        return model.result


class CallApiMixin(BaseApp):
    def test_api(self) -> ApiContext:
        return ApiContext(self)
