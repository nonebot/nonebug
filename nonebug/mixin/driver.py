from typing_extensions import final

import nonebot
from asgiref.typing import ASGIApplication
from async_asgi_testclient import TestClient

from nonebug.base import BaseApp, Context


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

    def get_client(self) -> TestClient:
        return self.client

    async def setup(self) -> None:
        await super().setup()
        await self.stack.enter_async_context(self.client)


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
        asgi = nonebot.get_asgi()
        return ServerContext(self, asgi=asgi)

    # def test_client(self):
    #     ...
