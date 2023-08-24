from typing import Union

import pytest
import nonebot
from nonebot.adapters import Bot, Event, Adapter, Message, MessageSegment
from nonebot.drivers import URL, Driver, Request, Response, HTTPServerSetup

from nonebug import App


@pytest.mark.asyncio
async def test_driver(app: App):
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
            super().__init__(driver, **kwargs)
            setup = HTTPServerSetup(URL("/test"), "POST", "test", self.handle)
            self.setup_http_server(setup)

        @classmethod
        def get_name(cls) -> str:
            return "fake"

        async def handle(self, request: Request) -> Response:
            assert request.content == b"test"
            bot = FakeBot(self, "test")
            result = await bot.call_api("test", test="test")
            assert result == "result"
            return Response(200, content="test")

        async def _call_api(self, bot: Bot, api: str, **data):
            assert bot.self_id == "test"
            assert api == "test"
            assert data == {"test": "test"}
            return "result"

    driver = nonebot.get_driver()
    driver.register_adapter(FakeAdapter)

    async with app.test_server() as ctx:
        client = ctx.get_client()

        res = await client.post("/test", data="test")
        assert res.status_code == 200
        assert res.text == "test"
