from typing import Optional

from nonebot.matcher import matchers

from .provider import NoneBugProvider


class Context:
    def __init__(self, app: "BaseApp", *args, **kwargs):
        self.app = app
        if self.app.context is not None:
            raise RuntimeError("Another test context is actived")
        self.app.context = self

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.run()

    async def run_test(self) -> None:
        pass

    async def cleanup(self) -> None:
        pass

    async def run(self) -> None:
        try:
            await self.run_test()
            await self.cleanup()
        finally:
            self.app.context = None


class BaseApp:
    def __init__(self):
        self.context: Optional[Context] = None
        if not isinstance(matchers.provider, NoneBugProvider):
            raise RuntimeError("NoneBug is not initialized")
        self.provider = matchers.provider
