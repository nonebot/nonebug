import contextlib
from typing import Optional
from typing_extensions import Self

from nonebot.matcher import matchers

from .provider import NoneBugProvider


class Context:
    def __init__(self, app: "BaseApp", *args, **kwargs):
        self.app = app
        if self.app.context is not None:
            raise RuntimeError("Another test context is actived")
        self.app.context = self

        self.stack = contextlib.AsyncExitStack()

    async def __aenter__(self) -> Self:
        await self.stack.__aenter__()
        await self.setup()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.run()
        finally:
            await self.stack.__aexit__(exc_type, exc_val, exc_tb)
            self.app.context = None

    async def setup(self) -> None:
        pass

    async def run(self) -> None:
        pass


class BaseApp:
    def __init__(self):
        self.context: Optional[Context] = None
        if not isinstance(matchers.provider, NoneBugProvider):
            raise RuntimeError("NoneBug is not initialized")
        self.provider = matchers.provider
