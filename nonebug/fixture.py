import pytest
import nonebot
from nonebot.matcher import matchers

from nonebug.app import App
from nonebug.provider import NoneBugProvider


@pytest.fixture(scope="session", autouse=True)
def nonebug_init(request: pytest.FixtureRequest) -> None:
    """
    Initialize nonebot before test case running.
    """

    nonebot.init(**getattr(request, "param", {}))
    matchers.set_provider(NoneBugProvider)


@pytest.fixture(name="app")
def nonebug_app() -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    return App()


__all__ = ["nonebug_init", "nonebug_app"]
