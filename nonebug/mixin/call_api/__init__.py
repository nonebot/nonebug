from queue import Queue
from typing import TYPE_CHECKING, Any, Dict, Type, Union, Optional

import pytest

from nonebug.base import BaseApp, Context

from .model import Api, Send, Model
from .fake import make_fake_bot, make_fake_adapter

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment


class ApiContext(Context):
    def __init__(self, app: BaseApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.wait_list: Queue[Model] = Queue()

    def create_adapter(self, *, base: Optional[Type["Adapter"]] = None) -> "Adapter":
        from nonebot import get_driver

        return make_fake_adapter(base=base)(get_driver(), self)

    def create_bot(
        self,
        *,
        base: Optional[Type["Bot"]] = None,
        adapter: Optional["Adapter"] = None,
        self_id: str = "test",
    ) -> "Bot":
        from nonebot import get_driver

        adapter = adapter or make_fake_adapter()(get_driver(), self)
        return make_fake_bot(base=base)(adapter, self_id)

    def mock_adapter(self, monkeypatch: pytest.MonkeyPatch, adapter: "Adapter") -> None:
        new_adapter = self.create_adapter()
        for attr in ("ctx", "_call_api"):
            monkeypatch.setattr(
                adapter, attr, getattr(new_adapter, attr), raising=False
            )

    def mock_bot(self, monkeypatch: pytest.MonkeyPatch, bot: "Bot") -> None:
        new_bot = self.create_bot()
        for attr in ("ctx", "send"):
            monkeypatch.setattr(bot, attr, getattr(new_bot, attr), raising=False)

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

    def got_call_api(self, api: str, **data: Any) -> Any:
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
