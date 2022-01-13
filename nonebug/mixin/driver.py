from typing_extensions import final
from typing import TypeVar, Optional

import pytest
from asgiref.typing import ASGIApplication
from async_asgi_testclient import TestClient

from nonebug.base import BaseApp

from .call_api import ApiContext

DC = TypeVar("DC", bound="DriverContext")


class DriverContext(ApiContext):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ctx = self.app.monkeypatch.context()
        self.m: Optional[pytest.MonkeyPatch] = None

    @property
    def monkeypatch(self) -> pytest.MonkeyPatch:
        if not self.m:
            raise RuntimeError("Monkeypatch only available in test context")
        return self.m

    async def __aenter__(self: DC) -> DC:
        self.m = self.ctx.__enter__()
        self.prepare_adapter()
        self.prepare_bot()
        return await super().__aenter__()

    def prepare_adapter(self):
        import nonebot

        driver = nonebot.get_driver()
        for adapter in driver._adapters.values():
            self.mock_adapter(self.monkeypatch, adapter)

    def prepare_bot(self):
        import nonebot
        from nonebot.adapters import Bot

        driver = nonebot.get_driver()
        origin = driver._bot_connect

        def _mocked_bot_connect(bot: Bot):
            self.mock_bot(self.monkeypatch, bot)
            origin(bot)

        self.monkeypatch.setattr(driver, "_bot_connect", _mocked_bot_connect)

    async def run_test(self):
        await super().run_test()
        self.ctx.__exit__(None, None, None)
        self.m = None


@final
class ServerContext(DriverContext):
    def __init__(
        self,
        app: BaseApp,
        *args,
        asgi: ASGIApplication,
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.asgi = asgi
        self.client = TestClient(self.asgi)

    async def __aenter__(self):
        await self.client.__aenter__()
        return await super().__aenter__()

    def get_client(self) -> TestClient:
        return self.client

    async def run_test(self):
        await super().run_test()
        await self.client.__aexit__(None, None, None)


# @final
# class ClientContext(DriverContext):
#     def __init__(
#         self,
#         app: BaseApp,
#         *args,
#         **kwargs,
#     ):
#         super().__init__(app, *args, **kwargs)
#         self.server = self.app.httpserver

#     def get_server(self) -> HTTPServer:
#         return self.server

#     async def run_test(self):
#         self.server.clear()


class DriverMixin(BaseApp):
    def test_server(self) -> ServerContext:
        import nonebot

        asgi = nonebot.get_asgi()
        return ServerContext(self, asgi=asgi, monkeypatch=self.monkeypatch)

    # def test_client(self):
    #     ...
