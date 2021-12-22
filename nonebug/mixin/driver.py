import pytest
from asgiref.typing import ASGIApplication
from async_asgi_testclient import TestClient

from nonebug.base import BaseApp

from .call_api import ApiContext


class AsgiContext(ApiContext):
    def __init__(
        self,
        app: BaseApp,
        *args,
        asgi: ASGIApplication,
        monkeypatch: pytest.MonkeyPatch,
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.asgi = asgi
        self.monkeypatch = monkeypatch
        self.client = TestClient(self.asgi)
        self.prepare_adapter()
        self.prepare_bot()

    async def __aenter__(self):
        await self.client.__aenter__()
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

    def get_client(self) -> TestClient:
        return self.client

    async def run_test(self):
        await self.client.__aexit__(None, None, None)
        self.monkeypatch.undo()


class DriverMixin(BaseApp):
    def test_asgi(self, monkeypatch: pytest.MonkeyPatch) -> AsgiContext:
        import nonebot

        asgi = nonebot.get_asgi()
        return AsgiContext(self, asgi=asgi, monkeypatch=monkeypatch)
