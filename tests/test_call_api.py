import pytest
from nonebot import get_bots
from utils import make_fake_event
from nonebot.adapters import Bot, Adapter

from nonebug import App
from nonebug.fixture import *


@pytest.mark.asyncio
async def test_should_call_api(app: App):
    async with app.test_api() as ctx:
        api = ctx.should_call_api("test", {"data": "data"}, "result")
        queue = ctx.wait_list
        assert not queue.empty()
        assert api == queue.get()
        assert (
            api.name == "test"
            and api.data == {"data": "data"}
            and api.result == "result"
        )


@pytest.mark.asyncio
async def test_should_call_send(app: App):
    from nonebot.adapters import Event, Message

    class FakeEvent(Event):
        def get_type(self) -> str:
            return "test"

        def get_event_name(self) -> str:
            return "test"

        def get_event_description(self) -> str:
            return "test"

        def get_user_id(self) -> str:
            return "test"

        def get_session_id(self) -> str:
            return "test"

        def get_message(self) -> Message:
            raise NotImplementedError

        def is_tome(self) -> bool:
            return True

        class Config:
            extra = "forbid"

    event = FakeEvent()
    async with app.test_api() as ctx:
        send = ctx.should_call_send(event, "test message", "result")
        queue = ctx.wait_list
        assert not queue.empty()
        assert send == queue.get()
        assert (
            send.event is event
            and send.message == "test message"
            and send.result == "result"
        )


@pytest.mark.asyncio
async def test_fake(app: App):
    class FakeAdapter(Adapter):
        ...

    class FakeBot(Bot):
        ...

    async with app.test_api() as ctx:
        adapter = ctx.create_adapter(base=FakeAdapter)
        assert isinstance(adapter, FakeAdapter)
        assert adapter.get_name() == "fake"
        bot = ctx.create_bot(base=FakeBot, self_id="test", adapter=adapter)
        assert isinstance(bot, FakeBot)
        assert bot.self_id == "test"


@pytest.mark.asyncio
async def test_got_call(app: App):
    async with app.test_api() as ctx:
        adapter = ctx.create_adapter()
        bot = ctx.create_bot(self_id="test", adapter=adapter)
        assert "test" in get_bots()
        api = ctx.should_call_api("test", {"key": "value"}, "result", adapter=adapter)
        result = await bot.call_api("test", key="value")
        assert ctx.wait_list.empty()
        assert result == "result"

    assert "test" not in get_bots()

    async with app.test_api() as ctx:
        bot = ctx.create_bot(self_id="test")
        assert "test" in get_bots()
        event = make_fake_event()()
        api = ctx.should_call_send(event, "test", "result", bot=bot, key="value")
        result = await bot.send(event, "test", key="value")
        assert ctx.wait_list.empty()
        assert result == "result"

    assert "test" not in get_bots()
