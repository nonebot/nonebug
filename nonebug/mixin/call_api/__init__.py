import contextlib
from queue import Queue
from typing import TYPE_CHECKING, Any, Union, TypeVar, Optional, overload

import pytest

from nonebug.base import BaseApp, Context

from .model import Api, Send, Model
from .fake import make_fake_bot, make_fake_adapter

if TYPE_CHECKING:
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment

A = TypeVar("A", bound="Adapter")
B = TypeVar("B", bound="Bot")


class ApiContext(Context):
    """API testing context.

    This context is used to test the api calling behavior of the bot.
    You may inherit this class to make api testing available in other context.

    Note:
        API testing needs to create new bots from `ApiContext.create_bot` or
        patch existing bots with `ApiContext.patch_bot`.

        Bots created from `ApiContext.create_bot` will be automatically connected
        to nonebot driver, and disconnected when the context is exited.
    """

    def __init__(self, app: BaseApp, *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.wait_list: Queue[Model] = Queue()
        self.connected_bot: set["Bot"] = set()

    def _connect_bot(self, adapter: "Adapter", bot: "Bot") -> None:
        adapter.bot_connect(bot)
        self.connected_bot.add(bot)

    @overload
    def create_adapter(
        self,
        *,
        base: None = None,
        **kwargs: Any,
    ) -> "Adapter": ...

    @overload
    def create_adapter(
        self,
        *,
        base: Optional[type[A]] = None,
        **kwargs: Any,
    ) -> A: ...

    def create_adapter(
        self,
        *,
        base: Optional[type[A]] = None,
        **kwargs: Any,
    ) -> Union[A, "Adapter"]:
        from nonebot import get_driver

        return make_fake_adapter(self, base=base)(get_driver(), **kwargs)

    @overload
    def create_bot(
        self,
        *,
        base: None = None,
        adapter: Optional["Adapter"] = None,
        self_id: str = "test",
        auto_connect: bool = True,
        **kwargs: Any,
    ) -> "Bot": ...

    @overload
    def create_bot(
        self,
        *,
        base: Optional[type[B]] = None,
        adapter: Optional["Adapter"] = None,
        self_id: str = "test",
        auto_connect: bool = True,
        **kwargs: Any,
    ) -> B: ...

    def create_bot(
        self,
        *,
        base: Optional[type[B]] = None,
        adapter: Optional["Adapter"] = None,
        self_id: str = "test",
        auto_connect: bool = True,
        **kwargs: Any,
    ) -> Union[B, "Bot"]:
        adapter = adapter or self.create_adapter()
        bot = make_fake_bot(self, base=base)(adapter, self_id, **kwargs)
        if auto_connect:
            self._connect_bot(adapter, bot)
        return bot

    def patch_adapter(
        self, monkeypatch: pytest.MonkeyPatch, adapter: "Adapter"
    ) -> None:
        new_adapter = self.create_adapter()
        monkeypatch.setattr(adapter.__class__, "_call_api", getattr(new_adapter.__class__, "_call_api"))

    def patch_bot(self, monkeypatch: pytest.MonkeyPatch, bot: "Bot") -> None:
        new_bot = self.create_bot(auto_connect=False)
        monkeypatch.setattr(bot, "send", getattr(new_bot, "send"))

    def should_call_api(
        self,
        api: str,
        data: dict[str, Any],
        result: Optional[Any] = None,
        exception: Optional[Exception] = None,
        adapter: Optional["Adapter"] = None,
    ) -> Api:
        model = Api(
            name=api, data=data, result=result, exception=exception, adapter=adapter
        )
        self.wait_list.put(model)
        return model

    def should_call_send(
        self,
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        result: Optional[Any] = None,
        exception: Optional[Exception] = None,
        bot: Optional["Bot"] = None,
        **kwargs: Any,
    ) -> Send:
        model = Send(
            event=event,
            message=message,
            kwargs=kwargs,
            result=result,
            exception=exception,
            bot=bot,
        )
        self.wait_list.put(model)
        return model

    def got_call_api(self, adapter: "Adapter", api: str, **data: Any) -> Any:
        if self.wait_list.empty():
            pytest.fail(
                f"Application has no api call but expected api={api} data={data}"
            )
        model = self.wait_list.get()
        if not isinstance(model, Api):
            pytest.fail(f"Application got api call {api} but expected {model}")
        if model.name != api:
            pytest.fail(f"Application got api call {api} but expected {model.name}")
        if model.data != data:
            pytest.fail(
                f"Application got api call {api} with "
                f"data {data} but expected {model.data}"
            )
        if model.adapter and model.adapter != adapter:
            pytest.fail(
                f"Application got api call {api} with "
                f"adapter {adapter} but expected {model.adapter}"
            )

        if model.exception is not None:
            raise model.exception
        return model.result

    def got_call_send(
        self,
        bot: "Bot",
        event: "Event",
        message: Union[str, "Message", "MessageSegment"],
        **kwargs: Any,
    ) -> Any:
        from nonebot.compat import model_dump

        if self.wait_list.empty():
            pytest.fail(
                "Application has no send call but expected "
                f"event={event} message={message} kwargs={kwargs}"
            )
        model = self.wait_list.get()
        if not isinstance(model, Send):
            pytest.fail(f"Application got send call but expected {model}")
        if model_dump(model.event) != model_dump(event):
            pytest.fail(
                "Application got send call with "
                f"event {event} but expected {model.event}"
            )
        if model.message != message:
            pytest.fail(
                "Application got send call with "
                f"message {message} but expected {model.message}"
            )
        if model.kwargs != kwargs:
            pytest.fail(
                "Application got send call with "
                f"kwargs {kwargs} but expected {model.kwargs}"
            )
        if model.bot and model.bot != bot:
            pytest.fail(
                f"Application got send call with bot {bot} but expected {model.bot}"
            )

        if model.exception is not None:
            raise model.exception
        return model.result

    @contextlib.contextmanager
    def _prepare_api_context(self):
        with pytest.MonkeyPatch.context() as m:
            self._prepare_adapters(m)
            self._prepare_bots(m)
            try:
                yield
            finally:
                while self.connected_bot:
                    bot = self.connected_bot.pop()
                    bot.adapter.bot_disconnect(bot)

    def _prepare_adapters(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from nonebot import get_driver

        for adapter in get_driver()._adapters.values():
            self.patch_adapter(monkeypatch, adapter)

    def _prepare_bots(self, monkeypatch: pytest.MonkeyPatch) -> None:
        from nonebot import get_bots

        for bot in get_bots().values():
            self.patch_bot(monkeypatch, bot)

    async def setup(self):
        await super().setup()
        self.stack.enter_context(self._prepare_api_context())

    async def run(self) -> None:
        await super().run()
        if not self.wait_list.empty():
            pytest.fail(
                f"Application has {self.wait_list.qsize()} api/send call(s) not called"
            )


class CallApiMixin(BaseApp):
    def test_api(self) -> ApiContext:
        return ApiContext(self)
