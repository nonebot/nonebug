from typing import Union

import pytest

from nonebug import App
from nonebug.fixture import *


@pytest.mark.asyncio
async def test_driver(app: App, monkeypatch: pytest.MonkeyPatch):
    import nonebot
    from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment
    from nonebot.drivers import URL, Driver, Request, Response, HTTPServerSetup

    class FakeBot(Bot):
        async def send(
            self,
            event: Event,
            message: Union[str, Message, MessageSegment],
            **kwargs,
        ):
            raise NotImplementedError

    class FakeAdapter(Adapter):
        def __init__(self, driver: Driver, **kwargs):
            super(FakeAdapter, self).__init__(driver, **kwargs)
            setup = HTTPServerSetup(URL("/test"), "POST", "test", self.handle)
            self.setup_http_server(setup)

        @classmethod
        def get_name(cls) -> str:
            return "fake"

        async def handle(self, request: Request) -> Response:
            assert request.content == b"test"
            bot = FakeBot(self, "test")
            self.bot_connect(bot)
            result = await bot.call_api("test", test="test")
            assert result == "result"
            return Response(200, content="test")

        async def _call_api(self, bot: Bot, api: str, **data):
            raise NotImplementedError

    driver = nonebot.get_driver()
    driver.register_adapter(FakeAdapter)

    async with app.test_asgi(monkeypatch) as ctx:
        client = ctx.get_client()

        ctx.should_call_api("test", data={"test": "test"}, result="result")
        res = await client.post("/test", data="test")
        assert res.status_code == 200
        assert res.text == "test"
