import pytest

from nonebug.app import App

from . import NONEBOT_INIT_KWARGS


@pytest.fixture(scope="session", autouse=True)
def nonebug_init(request: pytest.FixtureRequest) -> None:
    """
    Initialize nonebot before test case running.
    """
    import nonebot
    from nonebot.matcher import matchers

    from nonebug.provider import NoneBugProvider

    nonebot.init(**request.config.stash.get(NONEBOT_INIT_KWARGS, {}))
    matchers.set_provider(NoneBugProvider)


@pytest.fixture(name="app")
def nonebug_app(nonebug_init) -> App:
    """
    Get a test app provided by nonebug.
    Use app to define test cases and run them.
    """
    return App()


__all__ = ["nonebug_init", "nonebug_app"]
