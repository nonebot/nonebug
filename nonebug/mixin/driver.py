from typing_extensions import final

from asgiref.typing import ASGIApplication
from async_asgi_testclient import TestClient

from nonebug.base import BaseApp, Context

from .call_api import ApiContext


@final
class ServerContext(Context):
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
# class ClientContext(Context):
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
        return ServerContext(self, asgi=asgi)

    # def test_client(self):
    #     ...
