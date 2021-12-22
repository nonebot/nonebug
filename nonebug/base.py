from typing import Optional

import pytest


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

    async def run_test(self):
        pass

    async def run(self) -> None:
        try:
            await self.run_test()
        finally:
            self.app.context = None
            await self.app.reset()


class BaseApp:
    def __init__(self, monkeypatch: pytest.MonkeyPatch):
        self.context: Optional[Context] = None
        self.monkeypatch: pytest.MonkeyPatch = monkeypatch

    async def reset(self) -> None:
        pass
