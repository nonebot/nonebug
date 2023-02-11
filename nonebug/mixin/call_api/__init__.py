import contextlib
from queue import Queue
from typing import Any, Set, Dict, Type, Union, Optional

import pytest
from nonebot import get_bots, get_driver
from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

from nonebug.base import BaseApp, Context

from .model import Api, Send, Model
from .fake import make_fake_bot, make_fake_adapter


class ApiContext(Context):
    """API testing context.

    This context is used to test the api calling behavior of the bot.
    You may inherit this class to make api testing available in other context.

    Note:
        API testing need to create new bots from `ApiContext.create_bot` or
        patch existing bots with `ApiContext.mock_bot`.

        Bot created from `ApiContext.create_bot` will be automatically connected
        to nonebot driver, and disconnected when the context is exited.
    """

    def __init__(self, app: BaseApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.wait_list: Queue[Model] = Queue()
        self.connected_bot: Set[Bot] = set()

    def _connect_bot(self, bot: Bot) -> None:
        get_driver()._bot_connect(bot)
        self.connected_bot.add(bot)

    def create_adapter(
        self,
        *,
        base: Optional[Type[Adapter]] = None,
        **kwargs: Any,
    ) -> Adapter:
        return make_fake_adapter(self, base=base)(get_driver(), **kwargs)

    def create_bot(
        self,
        *,
        base: Optional[Type[Bot]] = None,
        adapter: Optional[Adapter] = None,
        self_id: str = "test",
        auto_connect: bool = True,
        **kwargs: Any,
    ) -> Bot:
        adapter = adapter or self.create_adapter()
        bot = make_fake_bot(self, base=base)(adapter, self_id, **kwargs)
        if auto_connect:
            self._connect_bot(bot)
        return bot

    def mock_adapter(self, monkeypatch: pytest.MonkeyPatch, adapter: Adapter) -> None:
        new_adapter = self.create_adapter()
        for attr in ("ctx", "_call_api"):
            monkeypatch.setattr(
                adapter, attr, getattr(new_adapter, attr), raising=False
            )

    def mock_bot(self, monkeypatch: pytest.MonkeyPatch, bot: Bot) -> None:
        new_bot = self.create_bot(auto_connect=False)
        for attr in ("ctx", "send"):
            monkeypatch.setattr(bot, attr, getattr(new_bot, attr), raising=False)

    def should_call_api(
        self,
        api: str,
        data: Dict[str, Any],
        result: Any,
        adapter: Optional[Adapter] = None,
    ) -> Api:
        model = Api(name=api, data=data, result=result, adapter=adapter)
        self.wait_list.put(model)
        return model

    def should_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        result: Any,
        bot: Optional[Bot] = None,
        **kwargs: Any,
    ) -> Send:
        model = Send(
            event=event, message=message, kwargs=kwargs, result=result, bot=bot
        )
        self.wait_list.put(model)
        return model

    def got_call_api(self, adapter: Adapter, api: str, **data: Any) -> Any:
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
        if model.adapter:
            assert (
                model.adapter == adapter
            ), f"Application got api call {api} with adapter {adapter} but expected {model.adapter}"
        return model.result

    def got_call_send(
        self,
        bot: Bot,
        event: Event,
        message: Union[str, Message, MessageSegment],
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
        if model.bot:
            assert (
                model.bot == bot
            ), f"Application got send call with bot {bot} but expected {model.bot}"
        return model.result

    @contextlib.contextmanager
    def _prepare(self):
        with pytest.MonkeyPatch.context() as m:
            self._prepare_adapters(m)
            self._prepare_bots(m)
            try:
                yield
            finally:
                while self.connected_bot:
                    bot = self.connected_bot.pop()
                    get_driver()._bot_disconnect(bot)

    def _prepare_adapters(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for adapter in get_driver()._adapters.values():
            self.mock_adapter(monkeypatch, adapter)

    def _prepare_bots(self, monkeypatch: pytest.MonkeyPatch) -> None:
        for bot in get_bots().values():
            self.mock_bot(monkeypatch, bot)

    async def setup(self):
        await super().setup()
        self.stack.enter_context(self._prepare())

    async def run(self) -> None:
        await super().run()
        assert (
            self.wait_list.empty()
        ), f"Application has {self.wait_list.qsize()} api/send call(s) not called"


class CallApiMixin(BaseApp):
    def test_api(self) -> ApiContext:
        return ApiContext(self)
