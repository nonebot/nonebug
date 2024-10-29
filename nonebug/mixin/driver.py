from typing import Optional
from typing_extensions import final

from asgiref.typing import ASGIApplication
from async_asgi_testclient import TestClient

from nonebug.base import BaseApp, Context


_global_client: Optional[TestClient] = None


def set_global_client(client: TestClient):
    global _global_client

    if _global_client is not None:
        raise RuntimeError()


def get_global_client() -> Optional[TestClient]:
    return _global_client


@final
class ServerContext(Context):
    def __init__(
        self,
        app: BaseApp,
        *args,
        asgi: ASGIApplication,
        client: Optional[TestClient] = None,
        **kwargs,
    ):
        super().__init__(app, *args, **kwargs)
        self.asgi = asgi
        self.specified_client = client
        self.client = TestClient(self.asgi)

    def get_client(self) -> TestClient:
        return self.specified_client or self.client

    async def setup(self) -> None:
        await super().setup()
        if self.specified_client is None:
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
    def test_server(self, asgi: Optional[ASGIApplication] = None) -> ServerContext:
        import nonebot

        client = None
        if asgi is None:
            client = get_global_client()

        asgi = asgi or nonebot.get_asgi()
        return ServerContext(self, asgi=asgi, client=client)

    # def test_client(self):
    #     ...
